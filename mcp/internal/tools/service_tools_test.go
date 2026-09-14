package tools

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
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
			registration.tool.Name == "search_posts" ||
			registration.tool.Name == "job_status" ||
			registration.tool.Name == "temporal_query" ||
			registration.tool.Name == "profile_history" ||
			registration.tool.Name == "coverage" ||
			registration.tool.Name == "maintenance_status"
		wantOpenWorld := registration.tool.Name == "query" ||
			registration.tool.Name == "refresh" ||
			registration.tool.Name == "topic" ||
			registration.tool.Name == "collection"
		if *annotations.ReadOnlyHint != wantReadOnly {
			t.Fatalf("%s readOnly = %v, want %v", registration.tool.Name, *annotations.ReadOnlyHint, wantReadOnly)
		}
		if *annotations.OpenWorldHint != wantOpenWorld {
			t.Fatalf("%s openWorld = %v, want %v", registration.tool.Name, *annotations.OpenWorldHint, wantOpenWorld)
		}
	}
	wantNames := []string{
		"service_info", "query", "search_posts", "refresh", "job_status", "topic",
		"temporal_query", "profile_history", "coverage", "collection",
		"maintenance_status",
	}
	if !reflect.DeepEqual(gotNames, wantNames) {
		t.Fatalf("tool names = %v, want %v", gotNames, wantNames)
	}
}

func TestSearchPostsBuildsStrictCacheOnlyContract(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"returned":2}`)}
	handler := makePostSearchHandler(fake)
	raw, readErr := os.ReadFile(filepath.Join(
		"..", "..", "..", "tests", "fixtures", "post_search_packet1.json",
	))
	if readErr != nil {
		t.Fatal(readErr)
	}
	var fixture struct {
		MCPArguments map[string]any `json:"mcp_arguments"`
	}
	if decodeErr := json.Unmarshal(raw, &fixture); decodeErr != nil {
		t.Fatal(decodeErr)
	}
	args := fixture.MCPArguments

	result, err := handler(context.Background(), callRequest(args))
	if err != nil || result.IsError || fake.postPath != "/v1/posts/search" {
		t.Fatalf("search result = %+v, path = %q, err = %v", result, fake.postPath, err)
	}
	if fake.postBody["profile_id"] != "default" ||
		fake.postBody["query"] != "reliable browser agents" ||
		fake.postBody["page_size"] != 20 ||
		fake.postBody["cursor"] != nil {
		t.Fatalf("search payload = %#v", fake.postBody)
	}
	filters := fake.postBody["filters"].(map[string]any)
	if !reflect.DeepEqual(filters["sources"], []string{"reddit", "x"}) ||
		filters["published_after"] != "2026-09-01T00:00:00Z" ||
		filters["published_before"] != "2026-09-13T23:59:59Z" {
		t.Fatalf("search filters = %#v", filters)
	}
	if fake.postBody["request_id"] == "" || textResult(result) != `{"returned":2}` {
		t.Fatalf("search result = %q, payload = %#v", textResult(result), fake.postBody)
	}

	for _, invalid := range []map[string]any{
		{},
		{"query": "---"},
		{"query": "x", "unknown": true},
		{"query": "x", "sources": []any{"reddit", "reddit"}},
		{"query": "x", "page_size": float64(101)},
		{"query": "x", "profile_id": "invalid profile"},
		{"query": "x", "published_after": "not-a-time"},
		{"query": "x", "published_after": "2026-09-14T00:00:00Z", "published_before": "2026-09-13T00:00:00Z"},
	} {
		invalidFake := &fakeService{}
		invalidResult, invalidErr := makePostSearchHandler(invalidFake)(
			context.Background(), callRequest(invalid),
		)
		if invalidErr != nil || invalidResult == nil || !invalidResult.IsError || invalidFake.postPath != "" {
			t.Fatalf("invalid args %#v: result = %+v, path = %q, err = %v", invalid, invalidResult, invalidFake.postPath, invalidErr)
		}
	}
}

func TestSearchPostsPacketTwoFiltersBrowseAndModes(t *testing.T) {
	data, err := os.ReadFile(filepath.Join("..", "..", "..", "tests", "fixtures", "post_search_packet2.json"))
	if err != nil {
		t.Fatal(err)
	}
	var fixture struct {
		Arguments map[string]any `json:"mcp_arguments"`
	}
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	fake := &fakeService{response: json.RawMessage(`{"returned":1}`)}
	result, err := makePostSearchHandler(fake)(context.Background(), callRequest(fixture.Arguments))
	if err != nil || result.IsError || fake.postPath != "/v1/posts/search" {
		t.Fatalf("result=%+v err=%v", result, err)
	}
	if fake.postBody["query"] != nil || fake.postBody["revision_mode"] != "all" || fake.postBody["sort"] != "observed_desc" {
		t.Fatalf("payload=%#v", fake.postBody)
	}
	filters := fake.postBody["filters"].(map[string]any)
	if len(filters) != 5 || !reflect.DeepEqual(filters["authors"], []string{"alice", "bob"}) || !reflect.DeepEqual(filters["topic_ids"], []string{"7"}) || !reflect.DeepEqual(filters["collection_refs"], []string{"legacy:spec:spec-1", "temporal:target:x-service:target-1"}) {
		t.Fatalf("filters=%#v", filters)
	}
	for _, invalid := range []map[string]any{
		{"query": nil}, {"query": ""}, {"query": "x", "authors": []any{}},
		{"query": "x", "topic_ids": []any{"7", "7"}},
		{"query": "x", "collection_refs": []any{"spec-1"}},
		{"query": "x", "collection_refs": []any{"temporal:target:unscoped"}},
		{"query": "x", "revision_mode": "latest"}, {"query": "x", "sort": ""},
		{"query": "x", "observed_after": nil},
		{"query": "x", "observed_after": "2026-09-09T00:00:00Z", "observed_before": "2026-09-08T00:00:00Z"},
	} {
		fake := &fakeService{}
		result, err := makePostSearchHandler(fake)(context.Background(), callRequest(invalid))
		if err != nil || !result.IsError || fake.postPath != "" {
			t.Fatalf("invalid=%#v result=%+v err=%v", invalid, result, err)
		}
	}
}

func TestSearchPostsPacketThreePreservesRankingAndCoverage(t *testing.T) {
	data, err := os.ReadFile(filepath.Join("..", "..", "..", "tests", "fixtures", "post_search_packet3.json"))
	if err != nil {
		t.Fatal(err)
	}
	var fixture struct {
		Arguments      map[string]any `json:"mcp_arguments"`
		RankingVersion string         `json:"ranking_version"`
	}
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	payload, err := json.Marshal(map[string]any{
		"coverage": map[string]any{"ranking_version": fixture.RankingVersion, "semantic": map[string]any{"mode": "stored_vectors_local_query"}},
		"hits":     []any{map[string]any{"matching_channels": []string{"semantic"}, "ranking": map[string]any{"version": fixture.RankingVersion}}},
	})
	if err != nil {
		t.Fatal(err)
	}
	fake := &fakeService{response: payload}
	result, err := makePostSearchHandler(fake)(context.Background(), callRequest(fixture.Arguments))
	if err != nil || result.IsError || textResult(result) != string(payload) || fake.postPath != "/v1/posts/search" {
		t.Fatalf("result=%+v path=%q err=%v", result, fake.postPath, err)
	}
}

func TestTemporalAndProfileToolsUseCompactIntelligenceBoundary(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"cache_only":true}`)}
	temporal := makeIntelligenceHandler(fake, "temporal_query")
	result, err := temporal(
		context.Background(),
		callRequest(map[string]any{
			"query":         "Acme timeline",
			"profile_id":    "linkedin-primary",
			"response_mode": "timeline",
			"as_of":         "2026-07-01T00:00:00Z",
		}),
	)
	if err != nil || result.IsError || fake.postPath != "/v1/intelligence" {
		t.Fatalf("temporal result = %+v, path = %q, err = %v", result, fake.postPath, err)
	}
	if fake.postBody["action"] != "temporal_query" ||
		fake.postBody["profile_id"] != "linkedin-primary" ||
		fake.postBody["response_mode"] != "timeline" {
		t.Fatalf("temporal payload = %#v", fake.postBody)
	}

	profile := makeIntelligenceHandler(fake, "profile_history")
	result, err = profile(
		context.Background(),
		callRequest(map[string]any{
			"profile_id": "linkedin-primary",
			"source":     "linkedin",
			"handle":     "alice",
			"limit":      float64(5),
		}),
	)
	if err != nil || result.IsError ||
		fake.postBody["action"] != "profile_history" ||
		fake.postBody["limit"] != 5 {
		t.Fatalf("profile result = %+v, payload = %#v, err = %v", result, fake.postBody, err)
	}
}

func TestCoverageCollectionAndMaintenanceUseServiceAuthority(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"status":"ready"}`)}
	for _, action := range []string{"coverage", "maintenance_status"} {
		handler := makeIntelligenceHandler(fake, action)
		result, err := handler(context.Background(), callRequest(nil))
		if err != nil || result.IsError || fake.postBody["action"] != action {
			t.Fatalf("%s result = %+v, payload = %#v, err = %v", action, result, fake.postBody, err)
		}
	}

	collection := makeIntelligenceHandler(fake, "collection")
	result, err := collection(
		context.Background(),
		callRequest(map[string]any{
			"operation":          "pause",
			"collection_spec_id": "linkedin-profiles",
		}),
	)
	if err != nil || result.IsError ||
		fake.postBody["operation"] != "pause" ||
		fake.postBody["collection_spec_id"] != "linkedin-profiles" {
		t.Fatalf("collection result = %+v, payload = %#v, err = %v", result, fake.postBody, err)
	}
}

func TestCollectionLifecycleExposesGetArchiveAndArchivedVisibility(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"status":"ready"}`)}
	handler := makeIntelligenceHandler(fake, "collection")
	for _, operation := range []string{"get", "archive"} {
		result, err := handler(
			context.Background(),
			callRequest(map[string]any{
				"operation":          operation,
				"collection_spec_id": "follow-x-list-agents",
			}),
		)
		if err != nil || result.IsError || fake.postBody["operation"] != operation ||
			fake.postBody["collection_spec_id"] != "follow-x-list-agents" {
			t.Fatalf("%s result = %+v, payload = %#v, err = %v", operation, result, fake.postBody, err)
		}
	}

	result, err := handler(
		context.Background(),
		callRequest(map[string]any{
			"operation":        "list",
			"include_archived": true,
		}),
	)
	if err != nil || result.IsError || fake.postBody["include_archived"] != true {
		t.Fatalf("list result = %+v, payload = %#v, err = %v", result, fake.postBody, err)
	}
}

func TestCachedQueryBuildsBoundedCacheOnlyContract(t *testing.T) {
	fake := &fakeService{response: json.RawMessage(`{"cache_status":"fresh"}`)}
	handler := makeQueryHandler(fake, false)
	args := map[string]any{
		"query":            "agent browser profiles",
		"profile_id":       "last30days-facebook",
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
	if fake.postBody["profile_id"] != "last30days-facebook" {
		t.Fatalf("profile_id = %v", fake.postBody["profile_id"])
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
		callRequest(map[string]any{
			"query":      "OpenAI",
			"profile_id": "last30days-facebook",
		}),
	)
	if err != nil || result.IsError {
		t.Fatalf("refresh result = %+v, err = %v", result, err)
	}
	if fake.postBody["freshness_policy"] != "force_refresh" {
		t.Fatalf("refresh freshness = %v", fake.postBody["freshness_policy"])
	}
	if fake.postBody["profile_id"] != "last30days-facebook" {
		t.Fatalf("refresh profile_id = %v", fake.postBody["profile_id"])
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
		{"query": "x", "profile_id": ""},
		{"query": "x", "profile_id": "invalid profile"},
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
