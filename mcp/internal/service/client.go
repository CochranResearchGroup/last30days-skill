// Package service provides the bounded Unix-socket HTTP client used by MCP.
package service

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	servicecontracts "github.com/mvanhorn/last30days-skill/mcp/internal/contracts"
)

const (
	// SocketEnvOverride is the shared Python/Go user-scoped socket override.
	SocketEnvOverride = "LAST30DAYS_SERVICE_SOCKET"
	// DefaultTimeout bounds local service calls without imposing crawl timeouts.
	DefaultTimeout = 10 * time.Second
	// MaxResponseBytes mirrors the Python service's transport bound.
	MaxResponseBytes = 131_072
)

// Client talks HTTP/1.1 over one local Unix domain socket.
type Client struct {
	SocketPath string
	Timeout    time.Duration
	Bootstrap  func(context.Context, string) error
}

// DefaultSocketPath follows the service runtime's user-scoped resolution.
func DefaultSocketPath() (string, error) {
	if override := strings.TrimSpace(os.Getenv(SocketEnvOverride)); override != "" {
		if !filepath.IsAbs(override) {
			return "", errors.New("service socket override must be an absolute path")
		}
		return override, nil
	}
	if runtimeDir := strings.TrimSpace(os.Getenv("XDG_RUNTIME_DIR")); runtimeDir != "" {
		if !filepath.IsAbs(runtimeDir) {
			return "", errors.New("XDG_RUNTIME_DIR must be an absolute path")
		}
		return filepath.Join(runtimeDir, "last30days", "service.sock"), nil
	}
	runUser := filepath.Join("/run/user", fmt.Sprintf("%d", os.Geteuid()))
	if info, err := os.Stat(runUser); err == nil && info.IsDir() {
		return filepath.Join(runUser, "last30days", "service.sock"), nil
	}
	return "", fmt.Errorf("%s or XDG_RUNTIME_DIR is required", SocketEnvOverride)
}

// Get returns one compact validated JSON object.
func (c *Client) Get(ctx context.Context, path string) (json.RawMessage, error) {
	return c.do(ctx, http.MethodGet, path, nil)
}

// Post returns one compact validated JSON object.
func (c *Client) Post(
	ctx context.Context,
	path string,
	payload any,
) (json.RawMessage, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("encode service request: %w", err)
	}
	return c.do(ctx, http.MethodPost, path, body)
}

func (c *Client) do(
	ctx context.Context,
	method string,
	path string,
	body []byte,
) (json.RawMessage, error) {
	socketPath := strings.TrimSpace(c.SocketPath)
	if socketPath == "" {
		var err error
		socketPath, err = DefaultSocketPath()
		if err != nil {
			return nil, err
		}
	}
	if !filepath.IsAbs(socketPath) {
		return nil, errors.New("service socket path must be absolute")
	}
	if !strings.HasPrefix(path, "/v1/") {
		return nil, errors.New("service path must be under /v1/")
	}
	info, err := os.Lstat(socketPath)
	if err != nil {
		bootstrap := c.Bootstrap
		if bootstrap == nil {
			bootstrap = BootstrapPackagedService
		}
		if bootstrapErr := bootstrap(ctx, socketPath); bootstrapErr != nil {
			return nil, errors.New("local intelligence service is unavailable")
		}
		info, err = os.Lstat(socketPath)
		if err != nil {
			return nil, errors.New("local intelligence service is unavailable")
		}
	}
	if info.Mode()&os.ModeSymlink != 0 || info.Mode()&os.ModeSocket == 0 {
		return nil, errors.New("service socket path is not a Unix socket")
	}

	timeout := c.Timeout
	if timeout <= 0 {
		timeout = DefaultTimeout
	}
	transport := &http.Transport{
		DialContext: func(
			dialCtx context.Context,
			_, _ string,
		) (net.Conn, error) {
			var dialer net.Dialer
			return dialer.DialContext(dialCtx, "unix", socketPath)
		},
		DisableKeepAlives: true,
	}
	defer transport.CloseIdleConnections()
	httpClient := &http.Client{Transport: transport, Timeout: timeout}

	var requestBody io.Reader
	if body != nil {
		requestBody = bytes.NewReader(body)
	}
	request, err := http.NewRequestWithContext(
		ctx,
		method,
		"http://last30days.local"+path,
		requestBody,
	)
	if err != nil {
		return nil, errors.New("construct local service request")
	}
	if body != nil {
		request.Header.Set("Content-Type", "application/json")
	}
	response, err := httpClient.Do(request)
	if err != nil {
		return nil, errors.New("local intelligence service is unavailable")
	}
	defer response.Body.Close()
	if response.Header.Get("X-Last30days-Contract-SHA256") !=
		servicecontracts.CatalogSHA256 {
		return nil, errors.New("local service contract is incompatible")
	}
	raw, err := io.ReadAll(io.LimitReader(response.Body, MaxResponseBytes+1))
	if err != nil {
		return nil, errors.New("read local service response")
	}
	if len(raw) > MaxResponseBytes {
		return nil, errors.New("local service response exceeded its size limit")
	}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return nil, safeHTTPError(response.StatusCode, raw)
	}
	var object map[string]any
	if err := json.Unmarshal(raw, &object); err != nil || object == nil {
		return nil, errors.New("local service returned invalid JSON")
	}
	var compact bytes.Buffer
	if err := json.Compact(&compact, raw); err != nil {
		return nil, errors.New("local service returned invalid JSON")
	}
	return json.RawMessage(compact.Bytes()), nil
}

// BootstrapPackagedService starts the service runtime shipped beside the MCP
// binary and waits for its singleton Unix socket. It never launches a crawl.
func BootstrapPackagedService(ctx context.Context, socketPath string) error {
	runtimeScript := strings.TrimSpace(os.Getenv("LAST30DAYS_SERVICE_RUNTIME"))
	if runtimeScript == "" {
		executable, err := os.Executable()
		if err != nil {
			return errors.New("locate MCP executable")
		}
		runtimeScript = filepath.Clean(
			filepath.Join(
				filepath.Dir(executable),
				"..",
				"runtime",
				"last30days",
				"scripts",
				"service.py",
			),
		)
	}
	if !filepath.IsAbs(runtimeScript) {
		return errors.New("packaged service runtime must be an absolute path")
	}
	info, err := os.Lstat(runtimeScript)
	if err != nil ||
		info.Mode()&os.ModeSymlink != 0 ||
		!info.Mode().IsRegular() {
		return errors.New("packaged service runtime is unavailable")
	}
	python := strings.TrimSpace(os.Getenv("LAST30DAYS_SERVICE_PYTHON"))
	if python == "" {
		python = "python3"
	}
	command := exec.Command(
		python,
		runtimeScript,
		"serve",
		"--socket",
		socketPath,
	)
	command.Stdin = nil
	command.Stdout = nil
	command.Stderr = nil
	command.Env = packagedServiceEnvironment()
	command.SysProcAttr = &syscall.SysProcAttr{Setsid: true}
	if err := command.Start(); err != nil {
		return errors.New("start packaged intelligence service")
	}
	_ = command.Process.Release()
	deadline := time.NewTimer(3 * time.Second)
	defer deadline.Stop()
	ticker := time.NewTicker(50 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return errors.New("service bootstrap cancelled")
		case <-deadline.C:
			return errors.New("service bootstrap timed out")
		case <-ticker.C:
			socketInfo, statErr := os.Lstat(socketPath)
			if statErr == nil &&
				socketInfo.Mode()&os.ModeSymlink == 0 &&
				socketInfo.Mode()&os.ModeSocket != 0 {
				return nil
			}
		}
	}
}

func packagedServiceEnvironment() []string {
	home, _ := os.UserHomeDir()
	pathParts := []string{
		filepath.Join(home, ".local", "bin"),
		filepath.Join(home, ".linuxbrew", "bin"),
		"/home/linuxbrew/.linuxbrew/bin",
		"/usr/local/bin",
		"/usr/bin",
		"/bin",
	}
	environment := []string{
		"HOME=" + home,
		"PATH=" + strings.Join(pathParts, ":"),
		"PYTHONUTF8=1",
	}
	for _, name := range []string{
		"LANG",
		"LC_ALL",
		"XDG_CONFIG_HOME",
		"XDG_DATA_HOME",
		"LAST30DAYS_CONFIG_DIR",
		"LAST30DAYS_SERVICE_DB",
	} {
		if value := strings.TrimSpace(os.Getenv(name)); value != "" {
			environment = append(environment, name+"="+value)
		}
	}
	return environment
}

func safeHTTPError(status int, raw []byte) error {
	var payload struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	}
	if err := json.Unmarshal(raw, &payload); err == nil {
		code := strings.TrimSpace(payload.Code)
		message := strings.TrimSpace(payload.Message)
		if len(code) > 64 {
			code = code[:64]
		}
		if len(message) > 256 {
			message = message[:256]
		}
		if code != "" && message != "" {
			return fmt.Errorf("local service HTTP %d: %s: %s", status, code, message)
		}
	}
	return fmt.Errorf("local service HTTP %d", status)
}

// JobPath safely places an opaque job ID into the service path.
func JobPath(jobID string) string {
	return "/v1/jobs/" + url.PathEscape(jobID)
}
