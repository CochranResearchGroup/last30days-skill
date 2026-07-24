package tools

import (
	"context"
	"encoding/json"
	"reflect"
	"strings"
	"testing"

	mcplib "github.com/mark3labs/mcp-go/mcp"
)

type fakeService struct {
	getPath  string
	postPath string
	postBody map[string]any
	response json.RawMessage
	err      error
}

func (f *fakeService) Get(_ context.Context, path string) (json.RawMessage, error) {
	f.getPath = path
	return f.response, f.err
}

func (f *fakeService) Post(
	_ context.Context,
	path string,
	body any,
) (json.RawMessage, error) {
	f.postPath = path
	f.postBody = body.(map[string]any)
	return f.response, f.err
}

func callRequest(args map[string]any) mcplib.CallToolRequest {
	var request mcplib.CallToolRequest
	request.Params.Arguments = args
	return request
}

func textResult(result *mcplib.CallToolResult) string {
	if result == nil {
		return ""
	}
	var output strings.Builder
	for _, content := range result.Content {
		if text, ok := content.(mcplib.TextContent); ok {
			output.WriteString(text.Text)
		}
	}
	return output.String()
}

func TestToolSurfaceNamesAndAnnotations(t *testing.T) {
	registrations := toolRegistrations(&fakeService{})
	gotNames := make([]string, 0, len(registrations))
	for _, registration := range registrations {
		gotNames = append(gotNames, registration.tool.Name)
		annotations := registration.tool.Annotations
		if annotations.ReadOnlyHint == nil ||
			annotations.IdempotentHint == nil ||
			annotations.OpenWorldHint == nil {
			t.Fatalf("%s is missing required annotations", registration.tool.Name)
		}
		if !*annotations.IdempotentHint {
			t.Fatalf("%s is not idempotent", registration.tool.Name)
		}
		wantReadOnly := registration.tool.Name == "service_info" ||
			registration.tool.Name == "job_status"
		wantOpenWorld := registration.tool.Name == "query" ||
			registration.tool.Name == "refresh" ||
			registration.tool.Name == "topic"
		if *annotations.ReadOnlyHint != wantReadOnly {
			t.Fatalf("%s readOnly = %v, want %v", registration.tool.Name, *annotations.ReadOnlyHint, wantReadOnly)
		}
		if *annotations.OpenWorldHint != wantOpenWorld {
			t.Fatalf("%s openWorld = %v, want %v", registration.tool.Name, *annotations.OpenWorldHint, wantOpenWorld)
		}
	}
	wantNames := []string{"service_info", "query", "refresh", "job_status", "topic"}
	if !reflect.DeepEqual(gotNames, wantNames) {
		t.Fatalf("tool names = %v, want %v", gotNames, wantNames)
	}
}

func TestCachedQueryBuildsBoundedCacheOnlyContract(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"cache_status":"fresh"}`)}
	handler := makeQueryHandler(fake, false)
	args := map[string]any{
		"query":            "agent browser profiles",
		"freshness_policy": "cache_only",
		"response_mode":    "brief",
		"sources":          []any{"x", "youtube", "x"},
		"topic_ids":        []any{"42"},
		"published_after":  "2026-07-01T00:00:00Z",
		"top_k":            float64(4),
		"max_chars":        float64(4096),
	}

	result, err := handler(context.Background(), callRequest(args))
	if err != nil || result.IsError {
		t.Fatalf("query result = %+v, err = %v", result, err)
	}
	if fake.postPath != "/v1/query" {
		t.Fatalf("post path = %q", fake.postPath)
	}
	if fake.postBody["freshness_policy"] != "cache_only" {
		t.Fatalf("freshness = %v", fake.postBody["freshness_policy"])
	}
	filters := fake.postBody["filters"].(map[string]any)
	if !reflect.DeepEqual(filters["sources"], []string{"x", "youtube"}) {
		t.Fatalf("sources = %#v", filters["sources"])
	}
	if !reflect.DeepEqual(filters["topic_ids"], []string{"42"}) ||
		filters["published_after"] != "2026-07-01T00:00:00Z" {
		t.Fatalf("filters = %#v", filters)
	}
	if fake.postBody["request_id"] == "" {
		t.Fatal("request_id is empty")
	}
	if textResult(result) != `{"cache_status":"fresh"}` {
		t.Fatalf("tool text = %q", textResult(result))
	}

	firstID := fake.postBody["request_id"]
	_, _ = handler(context.Background(), callRequest(args))
	if fake.postBody["request_id"] != firstID {
		t.Fatal("same query did not produce a stable request ID")
	}
}

func TestRefreshForcesRefreshAndJobStatusEscapesOpaqueID(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"job_id":"job/one"}`)}
	refresh := makeQueryHandler(fake, true)
	result, err := refresh(
		context.Background(),
		callRequest(map[string]any{"query": "OpenAI"}),
	)
	if err != nil || result.IsError {
		t.Fatalf("refresh result = %+v, err = %v", result, err)
	}
	if fake.postBody["freshness_policy"] != "force_refresh" {
		t.Fatalf("refresh freshness = %v", fake.postBody["freshness_policy"])
	}

	poll := makeJobStatusHandler(fake)
	result, err = poll(
		context.Background(),
		callRequest(map[string]any{"job_id": "job/one"}),
	)
	if err != nil || result.IsError {
		t.Fatalf("poll result = %+v, err = %v", result, err)
	}
	if fake.getPath != "/v1/jobs/job%2Fone" {
		t.Fatalf("poll path = %q", fake.getPath)
	}
}

func TestHandlersRejectInvalidArgumentsWithoutCallingService(t *testing.T) {
	fake := &fakeService{}
	query := makeQueryHandler(fake, false)
	cases := []map[string]any{
		{},
		{"query": "x", "freshness_policy": "force_refresh"},
		{"query": "x", "top_k": float64(1.5)},
		{"query": "x", "max_chars": float64(100)},
		{"query": "x", "sources": []any{""}},
	}
	for _, args := range cases {
		result, err := query(context.Background(), callRequest(args))
		if err != nil || result == nil || !result.IsError {
			t.Fatalf("args %#v: result = %+v, err = %v", args, result, err)
		}
	}
	if fake.postPath != "" {
		t.Fatalf("invalid input called service path %q", fake.postPath)
	}
}

func TestServiceInfoToolAndResourceShareLiveAuthority(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"status":"ready"}`)}
	handler := makeServiceInfoHandler(fake)
	result, err := handler(context.Background(), callRequest(nil))
	if err != nil || result.IsError || fake.getPath != "/v1/service-info" {
		t.Fatalf("service_info result = %+v, path = %q, err = %v", result, fake.getPath, err)
	}

	resource := makeServiceResourceHandler(
		fake,
		serviceInfoURI,
		"/v1/capabilities",
	)
	var request mcplib.ReadResourceRequest
	request.Params.URI = serviceInfoURI
	contents, err := resource(context.Background(), request)
	if err != nil || len(contents) != 1 {
		t.Fatalf("resource contents = %+v, err = %v", contents, err)
	}
	text, ok := contents[0].(mcplib.TextResourceContents)
	if !ok || text.URI != serviceInfoURI || text.Text != `{"status":"ready"}` {
		t.Fatalf("resource = %#v", contents[0])
	}
	if fake.getPath != "/v1/capabilities" {
		t.Fatalf("resource path = %q", fake.getPath)
	}
}

func TestTopicHandlerUsesServiceAuthority(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"action":"create"}`)}
	handler := makeTopicHandler(fake)
	result, err := handler(
		context.Background(),
		callRequest(map[string]any{
			"action":         "create",
			"name":           "Browser service",
			"search_queries": []any{"agent browser"},
		}),
	)
	if err != nil || result.IsError || fake.postPath != "/v1/topic" {
		t.Fatalf("topic result = %+v, path = %q, err = %v", result, fake.postPath, err)
	}
	if fake.postBody["action"] != "create" || fake.postBody["name"] != "Browser service" {
		t.Fatalf("topic body = %#v", fake.postBody)
	}
}
