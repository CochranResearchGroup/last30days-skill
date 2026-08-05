package service

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"os"
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

func handshakePayload() map[string]any {
	return map[string]any{
		"schema_version":          1,
		"product":                 servicecontracts.ProductIdentity,
		"service_version":         "0.2.7",
		"service_api_version":     servicecontracts.ServiceAPIMin,
		"contract_schema_version": servicecontracts.SchemaVersion,
		"contract_sha256":         servicecontracts.CatalogSHA256,
		"database_schema_version": servicecontracts.DatabaseSchemaMin,
		"runtime_manifest_sha256": strings.Repeat("a", 64),
		"status":                  "ready",
	}
}

func withCompatibleHandshake(
	t *testing.T,
	handler http.Handler,
) http.Handler {
	t.Helper()
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path == "/v1/service-info" {
			if err := json.NewEncoder(writer).Encode(handshakePayload()); err != nil {
				t.Errorf("encode handshake: %v", err)
			}
			return
		}
		handler.ServeHTTP(writer, request)
	})
}

func TestPackagedServiceEnvironmentIsSanitized(t *testing.T) {
	t.Setenv("OPENAI_API_KEY", "must-not-cross-boundary")
	t.Setenv("LAST30DAYS_SERVICE_DB", "/tmp/service-test.db")
	t.Setenv("XDG_RUNTIME_DIR", "/tmp/runtime-test")
	t.Setenv("LAST30DAYS_SYSTEMCTL", "/tmp/fake-systemctl")
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
	if !strings.Contains(environment, "XDG_RUNTIME_DIR=/tmp/runtime-test") ||
		!strings.Contains(environment, "LAST30DAYS_SYSTEMCTL=/tmp/fake-systemctl") {
		t.Fatal("managed service controls were not preserved")
	}
}

func TestManagedBootstrapInvokesPackagedInstaller(t *testing.T) {
	socketPath := unixHTTPServer(t, http.NotFoundHandler())
	root := t.TempDir()
	installer := filepath.Join(root, "install.sh")
	artifact := filepath.Join(root, "last30days-service-0.2.7.tar.gz")
	logPath := filepath.Join(root, "installer.log")
	script := "#!/bin/sh\nprintf '%s\\n' \"$@\" > '" + logPath + "'\n"
	if err := os.WriteFile(installer, []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(artifact, []byte("artifact"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := bootstrapManagedService(
		context.Background(), socketPath, installer, artifact,
	); err != nil {
		t.Fatalf("bootstrapManagedService: %v", err)
	}
	raw, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatal(err)
	}
	arguments := strings.Split(strings.TrimSpace(string(raw)), "\n")
	want := []string{
		"install",
		"--artifact",
		artifact,
		"--socket",
		socketPath,
		"--timeout",
		"15",
	}
	if strings.Join(arguments, "\n") != strings.Join(want, "\n") {
		t.Fatalf("installer arguments = %#v, want %#v", arguments, want)
	}
}

func TestPackagedServicePayloadResolvesIndependentBundleLayout(t *testing.T) {
	root := t.TempDir()
	executable := filepath.Join(root, "bin", "last30days-pp-mcp")
	installer := filepath.Join(root, "runtime", "service", "scripts", "install.sh")
	artifact := filepath.Join(
		root,
		"runtime",
		"service",
		"artifacts",
		"last30days-service-0.2.7.tar.gz",
	)
	for _, path := range []string{executable, installer, artifact} {
		if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte("fixture"), 0o600); err != nil {
			t.Fatal(err)
		}
	}

	gotInstaller, gotArtifact, err := packagedServicePayload(executable)
	if err != nil {
		t.Fatal(err)
	}
	if gotInstaller != installer || gotArtifact != artifact {
		t.Fatalf(
			"payload = (%q, %q), want (%q, %q)",
			gotInstaller,
			gotArtifact,
			installer,
			artifact,
		)
	}
}

func TestClientHandshakeCompatibilityMatrix(t *testing.T) {
	cases := []struct {
		name         string
		mutate       func(map[string]any)
		headerDigest string
		wantState    string
	}{
		{"compatible", func(map[string]any) {}, servicecontracts.CatalogSHA256, compatibilityCompatible},
		{"product", func(p map[string]any) { p["product"] = "other" }, servicecontracts.CatalogSHA256, compatibilityProductMismatch},
		{"service api", func(p map[string]any) { p["service_api_version"] = 2 }, servicecontracts.CatalogSHA256, compatibilityServiceAPIUnsupported},
		{"contract schema", func(p map[string]any) { p["contract_schema_version"] = 2 }, servicecontracts.CatalogSHA256, compatibilityContractSchemaUnsupported},
		{"contract body", func(p map[string]any) { p["contract_sha256"] = strings.Repeat("b", 64) }, servicecontracts.CatalogSHA256, compatibilityContractDigestMismatch},
		{"contract header", func(map[string]any) {}, "stale", compatibilityContractDigestMismatch},
		{"database schema", func(p map[string]any) { p["database_schema_version"] = 16 }, servicecontracts.CatalogSHA256, compatibilityDatabaseSchemaUnsupported},
		{"runtime manifest", func(p map[string]any) { p["runtime_manifest_sha256"] = nil }, servicecontracts.CatalogSHA256, compatibilityRuntimeManifestInvalid},
		{"malformed", func(p map[string]any) {
			p["product"] = map[string]any{"private": "do not expose"}
			p["private"] = "do not expose"
		}, servicecontracts.CatalogSHA256, compatibilityHandshakeInvalid},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			ordinaryCalls := 0
			payload := handshakePayload()
			testCase.mutate(payload)
			socketPath := unixHTTPServer(t, http.HandlerFunc(func(
				writer http.ResponseWriter,
				request *http.Request,
			) {
				if request.URL.Path == "/v1/service-info" {
					if request.Header.Get("X-Last30days-MCP-Version") != "4.0.1" ||
						request.Header.Get("X-Last30days-Expected-Product") !=
							servicecontracts.ProductIdentity {
						t.Errorf("client handshake headers were not declared")
					}
					writer.Header().Set(
						"X-Last30days-Contract-SHA256",
						testCase.headerDigest,
					)
					_ = json.NewEncoder(writer).Encode(payload)
					return
				}
				ordinaryCalls++
				_, _ = writer.Write([]byte(`{"status":"ready"}`))
			}))
			client := &Client{
				SocketPath:     socketPath,
				AdapterVersion: "4.0.1",
			}

			raw, err := client.Get(context.Background(), "/v1/service-info")
			if err != nil {
				t.Fatalf("diagnostic handshake: %v", err)
			}
			var diagnostic map[string]any
			if err := json.Unmarshal(raw, &diagnostic); err != nil {
				t.Fatal(err)
			}
			if diagnostic["compatibility_state"] != testCase.wantState {
				t.Fatalf(
					"compatibility_state = %v, want %s",
					diagnostic["compatibility_state"],
					testCase.wantState,
				)
			}
			if diagnostic["mcp_adapter_version"] != "4.0.1" {
				t.Fatalf("adapter version = %v", diagnostic["mcp_adapter_version"])
			}
			if _, exposed := diagnostic["private"]; exposed {
				t.Fatal("diagnostic exposed an undeclared service field")
			}

			_, err = client.Get(context.Background(), "/v1/health")
			if testCase.wantState == compatibilityCompatible {
				if err != nil || ordinaryCalls != 1 {
					t.Fatalf("compatible call: calls=%d err=%v", ordinaryCalls, err)
				}
			} else if err == nil ||
				!strings.Contains(err.Error(), testCase.wantState) ||
				ordinaryCalls != 0 {
				t.Fatalf("incompatible call: calls=%d err=%v", ordinaryCalls, err)
			}
		})
	}
}

func TestClientUsesUnixHTTPAndReturnsCompactJSON(t *testing.T) {
	var method, path string
	var requestBody map[string]any
	socketPath := unixHTTPServer(t, withCompatibleHandshake(
		t,
		http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			method = request.Method
			path = request.URL.Path
			if request.Body != nil {
				_ = json.NewDecoder(request.Body).Decode(&requestBody)
			}
			writer.Header().Set("Content-Type", "application/json")
			_, _ = writer.Write([]byte("{\n  \"status\": \"ready\"\n}"))
		}),
	))
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
	socketPath := unixHTTPServer(t, withCompatibleHandshake(
		t,
		http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
			writer.WriteHeader(http.StatusBadRequest)
			_, _ = writer.Write([]byte(`{"code":"invalid_contract","message":"request contract is invalid","private":"do not expose"}`))
		}),
	))
	client := &Client{SocketPath: socketPath}

	_, err := client.Get(context.Background(), "/v1/health")

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

	socketPath := unixHTTPServer(
		t,
		withCompatibleHandshake(t, http.NotFoundHandler()),
	)
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
