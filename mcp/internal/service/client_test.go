package service

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"path/filepath"
	"strings"
	"testing"

	servicecontracts "github.com/mvanhorn/last30days-skill/mcp/internal/contracts"
)

func unixHTTPServer(
	t *testing.T,
	handler http.Handler,
) string {
	t.Helper()
	socketPath := filepath.Join(t.TempDir(), "service.sock")
	listener, err := net.Listen("unix", socketPath)
	if err != nil {
		t.Fatalf("listen: %v", err)
	}
	server := &http.Server{Handler: http.HandlerFunc(func(
		writer http.ResponseWriter,
		request *http.Request,
	) {
		writer.Header().Set(
			"X-Last30days-Contract-SHA256",
			servicecontracts.CatalogSHA256,
		)
		handler.ServeHTTP(writer, request)
	})}
	go func() {
		_ = server.Serve(listener)
	}()
	t.Cleanup(func() {
		_ = server.Close()
		_ = listener.Close()
	})
	return socketPath
}

func TestPackagedServiceEnvironmentIsSanitized(t *testing.T) {
	t.Setenv("OPENAI_API_KEY", "must-not-cross-boundary")
	t.Setenv("LAST30DAYS_SERVICE_DB", "/tmp/service-test.db")
	environment := strings.Join(packagedServiceEnvironment(), "\n")
	if strings.Contains(environment, "OPENAI_API_KEY") ||
		strings.Contains(environment, "must-not-cross-boundary") {
		t.Fatal("credential leaked into packaged service environment")
	}
	if !strings.Contains(
		environment,
		"LAST30DAYS_SERVICE_DB=/tmp/service-test.db",
	) {
		t.Fatal("safe service path override was not preserved")
	}
	if !strings.Contains(environment, ".local/bin") ||
		!strings.Contains(environment, ".linuxbrew/bin") {
		t.Fatal("sanitized worker PATH is incomplete")
	}
}

func TestClientRejectsIncompatibleServiceContract(t *testing.T) {
	socketPath := filepath.Join(t.TempDir(), "service.sock")
	listener, err := net.Listen("unix", socketPath)
	if err != nil {
		t.Fatal(err)
	}
	server := &http.Server{Handler: http.HandlerFunc(func(
		writer http.ResponseWriter,
		_ *http.Request,
	) {
		writer.Header().Set("X-Last30days-Contract-SHA256", "stale")
		_, _ = writer.Write([]byte(`{"status":"ready"}`))
	})}
	go func() { _ = server.Serve(listener) }()
	t.Cleanup(func() {
		_ = server.Close()
		_ = listener.Close()
	})

	_, err = (&Client{SocketPath: socketPath}).Get(
		context.Background(),
		"/v1/service-info",
	)
	if err == nil || !strings.Contains(err.Error(), "incompatible") {
		t.Fatalf("compatibility error = %v", err)
	}
}

func TestClientUsesUnixHTTPAndReturnsCompactJSON(t *testing.T) {
	var method, path string
	var requestBody map[string]any
	socketPath := unixHTTPServer(t, http.HandlerFunc(func(
		writer http.ResponseWriter,
		request *http.Request,
	) {
		method = request.Method
		path = request.URL.Path
		if request.Body != nil {
			_ = json.NewDecoder(request.Body).Decode(&requestBody)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte("{\n  \"status\": \"ready\"\n}"))
	}))
	client := &Client{SocketPath: socketPath}

	payload, err := client.Post(
		context.Background(),
		"/v1/query",
		map[string]any{"query": "OpenAI"},
	)

	if err != nil {
		t.Fatalf("Post: %v", err)
	}
	if method != http.MethodPost || path != "/v1/query" {
		t.Fatalf("request = %s %s", method, path)
	}
	if requestBody["query"] != "OpenAI" {
		t.Fatalf("body = %#v", requestBody)
	}
	if string(payload) != `{"status":"ready"}` {
		t.Fatalf("payload = %s", payload)
	}
}

func TestClientReturnsBoundedSafeServiceErrors(t *testing.T) {
	socketPath := unixHTTPServer(t, http.HandlerFunc(func(
		writer http.ResponseWriter,
		_ *http.Request,
	) {
		writer.WriteHeader(http.StatusBadRequest)
		_, _ = writer.Write([]byte(`{"code":"invalid_contract","message":"request contract is invalid","private":"do not expose"}`))
	}))
	client := &Client{SocketPath: socketPath}

	_, err := client.Get(context.Background(), "/v1/service-info")

	if err == nil ||
		!strings.Contains(err.Error(), "invalid_contract") ||
		strings.Contains(err.Error(), "private") {
		t.Fatalf("safe error = %v", err)
	}
}

func TestClientRejectsNonSocketAndNonV1Paths(t *testing.T) {
	client := &Client{SocketPath: filepath.Join(t.TempDir(), "missing.sock")}
	if _, err := client.Get(context.Background(), "/v1/health"); err == nil {
		t.Fatal("expected missing socket error")
	}

	socketPath := unixHTTPServer(t, http.NotFoundHandler())
	client.SocketPath = socketPath
	if _, err := client.Get(context.Background(), "/internal/debug"); err == nil {
		t.Fatal("expected non-v1 path error")
	}
}

func TestJobPathEscapesOpaqueIdentifier(t *testing.T) {
	if got := JobPath("job/one?debug=true"); got != "/v1/jobs/job%2Fone%3Fdebug=true" {
		t.Fatalf("JobPath = %q", got)
	}
}
