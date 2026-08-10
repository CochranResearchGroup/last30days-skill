// Package tools exposes the thin MCP surface over the local intelligence service.
package tools

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"regexp"
	"strings"

	mcplib "github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"

	servicecontracts "github.com/mvanhorn/last30days-skill/mcp/internal/contracts"
	serviceclient "github.com/mvanhorn/last30days-skill/mcp/internal/service"
)

const serviceInfoURI = "last30days://capabilities"

var profileIDPattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`)

// ServiceAPI is the narrow transport seam used by handlers and tests.
type ServiceAPI interface {
	Get(context.Context, string) (json.RawMessage, error)
	Post(context.Context, string, any) (json.RawMessage, error)
}

// Config injects a client. SocketPath is used only when Client is nil.
type Config struct {
	Client         ServiceAPI
	SocketPath     string
	AdapterVersion string
}

// Register adds the complete discoverable service surface.
func Register(s *server.MCPServer, cfg Config) {
	client := cfg.Client
	if client == nil {
		client = &serviceclient.Client{
			SocketPath:     cfg.SocketPath,
			AdapterVersion: cfg.AdapterVersion,
		}
	}
	for _, registration := range toolRegistrations(client) {
		s.AddTool(registration.tool, registration.handler)
	}
	for _, resource := range []struct {
		uri, name, description, path string
	}{
		{
			"last30days://capabilities",
			"last30days-capabilities",
			"Live service capabilities and limits.",
			"/v1/capabilities",
		},
		{
			"last30days://sources",
			"last30days-sources",
			"Live source readiness and indexed yield.",
			"/v1/sources",
		},
		{
			"last30days://topics",
			"last30days-topics",
			"Configured topics and schedule state.",
			"/v1/topics",
		},
	} {
		s.AddResource(
			mcplib.NewResource(
				resource.uri,
				resource.name,
				mcplib.WithResourceDescription(resource.description),
				mcplib.WithMIMEType("application/json"),
			),
			makeServiceResourceHandler(client, resource.uri, resource.path),
		)
	}
}

type toolRegistration struct {
	tool    mcplib.Tool
	handler server.ToolHandlerFunc
}

func commonAnnotations(readOnly, openWorld bool) []mcplib.ToolOption {
	return []mcplib.ToolOption{
		mcplib.WithReadOnlyHintAnnotation(readOnly),
		mcplib.WithDestructiveHintAnnotation(false),
		mcplib.WithIdempotentHintAnnotation(true),
		mcplib.WithOpenWorldHintAnnotation(openWorld),
		mcplib.WithSchemaAdditionalProperties(false),
	}
}

func toolRegistrations(client ServiceAPI) []toolRegistration {
	infoOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Discover live last30days service capabilities, source readiness, limits, and index status.",
		),
	}
	infoOptions = append(infoOptions, commonAnnotations(true, false)...)

	queryOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Query cached intelligence. The default prefer_cache policy may create or join a durable background refresh; select cache_only to prohibit external work.",
		),
		mcplib.WithString(
			"query",
			mcplib.Required(),
			mcplib.Description("Question or topic to retrieve from cached intelligence."),
			mcplib.MinLength(1),
			mcplib.MaxLength(4096),
		),
		mcplib.WithString(
			"profile_id",
			mcplib.Description("Authorized service profile whose public and private evidence partitions may be queried."),
			mcplib.MaxLength(128),
			mcplib.DefaultString("default"),
		),
		mcplib.WithString(
			"freshness_policy",
			mcplib.Description("Cache policy. cache_only guarantees no acquisition."),
			mcplib.Enum("prefer_cache", "cache_only", "refresh_if_stale"),
			mcplib.DefaultString("prefer_cache"),
		),
		mcplib.WithString(
			"response_mode",
			mcplib.Description("Return citation evidence or a compact extractive brief."),
			mcplib.Enum("evidence", "brief"),
			mcplib.DefaultString("evidence"),
		),
		mcplib.WithArray(
			"sources",
			mcplib.Description("Optional source names to include."),
			mcplib.WithStringItems(mcplib.MinLength(1), mcplib.MaxLength(64)),
			mcplib.MaxItems(32),
		),
		mcplib.WithArray(
			"topic_ids",
			mcplib.Description("Optional stable topic IDs to include."),
			mcplib.WithStringItems(mcplib.MinLength(1), mcplib.MaxLength(128)),
			mcplib.MaxItems(32),
		),
		mcplib.WithString(
			"published_after",
			mcplib.Description("Optional inclusive ISO-8601 lower publication bound."),
			mcplib.MaxLength(64),
		),
		mcplib.WithString(
			"published_before",
			mcplib.Description("Optional inclusive ISO-8601 upper publication bound."),
			mcplib.MaxLength(64),
		),
		mcplib.WithInteger(
			"top_k",
			mcplib.Description("Maximum evidence items."),
			mcplib.Min(1),
			mcplib.Max(100),
			mcplib.DefaultNumber(8),
		),
		mcplib.WithInteger(
			"max_chars",
			mcplib.Description("Maximum compact JSON response size."),
			mcplib.Min(512),
			mcplib.Max(65536),
			mcplib.DefaultNumber(8192),
		),
	}
	queryOptions = append(queryOptions, commonAnnotations(false, true)...)

	refreshOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Create or join an explicit force-refresh job, returning current cached evidence and a durable job ID.",
		),
		mcplib.WithString(
			"query",
			mcplib.Required(),
			mcplib.Description("Question or topic to refresh."),
			mcplib.MinLength(1),
			mcplib.MaxLength(4096),
		),
		mcplib.WithString(
			"profile_id",
			mcplib.Description("Authorized service profile to refresh and query."),
			mcplib.MaxLength(128),
			mcplib.DefaultString("default"),
		),
		mcplib.WithString(
			"response_mode",
			mcplib.Enum("evidence", "brief"),
			mcplib.DefaultString("evidence"),
		),
		mcplib.WithArray(
			"sources",
			mcplib.Description("Optional source names to acquire."),
			mcplib.WithStringItems(mcplib.MinLength(1), mcplib.MaxLength(64)),
			mcplib.MaxItems(32),
		),
		mcplib.WithInteger("top_k", mcplib.Min(1), mcplib.Max(100), mcplib.DefaultNumber(8)),
		mcplib.WithInteger(
			"max_chars",
			mcplib.Min(512),
			mcplib.Max(65536),
			mcplib.DefaultNumber(8192),
		),
	}
	refreshOptions = append(refreshOptions, commonAnnotations(false, true)...)

	pollOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Read the durable phase and source outcomes for one refresh job.",
		),
		mcplib.WithString(
			"job_id",
			mcplib.Required(),
			mcplib.Description("Opaque durable job ID returned by refresh or query."),
			mcplib.MinLength(1),
			mcplib.MaxLength(128),
		),
	}
	pollOptions = append(pollOptions, commonAnnotations(true, false)...)

	topicOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"List or manage service-owned topics, or request one scheduled refresh.",
		),
		mcplib.WithString(
			"action",
			mcplib.Required(),
			mcplib.Enum("list", "create", "update", "pause", "resume", "request_refresh"),
		),
		mcplib.WithString("topic_id", mcplib.MaxLength(128)),
		mcplib.WithString("name", mcplib.MaxLength(256)),
		mcplib.WithArray(
			"search_queries",
			mcplib.WithStringItems(mcplib.MinLength(1), mcplib.MaxLength(4096)),
			mcplib.MaxItems(32),
		),
		mcplib.WithString("schedule", mcplib.MaxLength(128)),
		mcplib.WithArray(
			"sources",
			mcplib.WithStringItems(mcplib.MinLength(1), mcplib.MaxLength(64)),
			mcplib.MaxItems(32),
		),
	}
	topicOptions = append(topicOptions, commonAnnotations(false, true)...)

	temporalOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Query cache-only temporal intelligence with explicit valid-time, knowledge-time, evidence, ambiguity, and projection receipts.",
		),
		mcplib.WithString(
			"query",
			mcplib.Required(),
			mcplib.MinLength(1),
			mcplib.MaxLength(4096),
		),
		mcplib.WithString(
			"profile_id",
			mcplib.Description("Authorized browser profile partition; default queries public evidence only."),
			mcplib.MaxLength(128),
			mcplib.DefaultString("default"),
		),
		mcplib.WithString(
			"response_mode",
			mcplib.Enum(
				"evidence", "brief", "timeline", "entity_dossier",
				"event_dossier", "trend", "comparison",
			),
			mcplib.DefaultString("evidence"),
		),
		mcplib.WithString("as_of", mcplib.MaxLength(64)),
		mcplib.WithString("during_from", mcplib.MaxLength(64)),
		mcplib.WithString("during_to", mcplib.MaxLength(64)),
		mcplib.WithString("known_as_of", mcplib.MaxLength(64)),
	}
	temporalOptions = append(temporalOptions, commonAnnotations(true, false)...)

	profileOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Read immutable source-profile history and section evidence without operating a browser.",
		),
		mcplib.WithString("profile_id", mcplib.MaxLength(128), mcplib.DefaultString("default")),
		mcplib.WithString("source", mcplib.MaxLength(64)),
		mcplib.WithString("handle", mcplib.MaxLength(256)),
		mcplib.WithInteger("limit", mcplib.Min(1), mcplib.Max(100), mcplib.DefaultNumber(20)),
	}
	profileOptions = append(profileOptions, commonAnnotations(true, false)...)

	coverageOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Read collection specs, attempted intervals, source yield, and unresolved gaps.",
		),
		mcplib.WithString("profile_id", mcplib.MaxLength(128), mcplib.DefaultString("default")),
	}
	coverageOptions = append(coverageOptions, commonAnnotations(true, false)...)

	collectionOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"List or govern typed recurring collection specs through the durable service authority.",
		),
		mcplib.WithString(
			"operation",
			mcplib.Required(),
			mcplib.Enum("list", "put", "pause", "resume", "run"),
		),
		mcplib.WithString("profile_id", mcplib.MaxLength(128), mcplib.DefaultString("default")),
		mcplib.WithObject(
			"spec",
			mcplib.Description("Complete versioned collection-spec contract for put."),
			mcplib.AdditionalProperties(true),
			mcplib.MaxProperties(32),
		),
		mcplib.WithString("collection_spec_id", mcplib.MaxLength(128)),
		mcplib.WithString("scheduled_for", mcplib.MaxLength(64)),
	}
	collectionOptions = append(collectionOptions, commonAnnotations(false, true)...)

	maintenanceOptions := []mcplib.ToolOption{
		mcplib.WithDescription(
			"Read bounded App Intelligence task receipts, graph projection state, and adapter-repair safety gates.",
		),
		mcplib.WithString("profile_id", mcplib.MaxLength(128), mcplib.DefaultString("default")),
	}
	maintenanceOptions = append(maintenanceOptions, commonAnnotations(true, false)...)

	return []toolRegistration{
		{
			tool:    mcplib.NewTool("service_info", infoOptions...),
			handler: makeServiceInfoHandler(client),
		},
		{
			tool:    mcplib.NewTool("query", queryOptions...),
			handler: makeQueryHandler(client, false),
		},
		{
			tool:    mcplib.NewTool("refresh", refreshOptions...),
			handler: makeQueryHandler(client, true),
		},
		{
			tool:    mcplib.NewTool("job_status", pollOptions...),
			handler: makeJobStatusHandler(client),
		},
		{
			tool:    mcplib.NewTool("topic", topicOptions...),
			handler: makeTopicHandler(client),
		},
		{
			tool:    mcplib.NewTool("temporal_query", temporalOptions...),
			handler: makeIntelligenceHandler(client, "temporal_query"),
		},
		{
			tool:    mcplib.NewTool("profile_history", profileOptions...),
			handler: makeIntelligenceHandler(client, "profile_history"),
		},
		{
			tool:    mcplib.NewTool("coverage", coverageOptions...),
			handler: makeIntelligenceHandler(client, "coverage"),
		},
		{
			tool:    mcplib.NewTool("collection", collectionOptions...),
			handler: makeIntelligenceHandler(client, "collection"),
		},
		{
			tool:    mcplib.NewTool("maintenance_status", maintenanceOptions...),
			handler: makeIntelligenceHandler(client, "maintenance_status"),
		},
	}
}

func makeServiceInfoHandler(client ServiceAPI) server.ToolHandlerFunc {
	return func(
		ctx context.Context,
		_ mcplib.CallToolRequest,
	) (*mcplib.CallToolResult, error) {
		payload, err := client.Get(ctx, "/v1/service-info")
		return toolResult(payload, err)
	}
}

func makeQueryHandler(client ServiceAPI, forceRefresh bool) server.ToolHandlerFunc {
	return func(
		ctx context.Context,
		req mcplib.CallToolRequest,
	) (*mcplib.CallToolResult, error) {
		payload, err := queryPayload(req.GetArguments(), forceRefresh)
		if err != nil {
			return mcplib.NewToolResultError(err.Error()), nil
		}
		response, err := client.Post(ctx, "/v1/query", payload)
		return toolResult(response, err)
	}
}

func makeJobStatusHandler(client ServiceAPI) server.ToolHandlerFunc {
	return func(
		ctx context.Context,
		req mcplib.CallToolRequest,
	) (*mcplib.CallToolResult, error) {
		jobID, err := requireString(req.GetArguments(), "job_id", 128)
		if err != nil {
			return mcplib.NewToolResultError(err.Error()), nil
		}
		payload, err := client.Get(ctx, serviceclient.JobPath(jobID))
		return toolResult(payload, err)
	}
}

func makeTopicHandler(client ServiceAPI) server.ToolHandlerFunc {
	return func(
		ctx context.Context,
		req mcplib.CallToolRequest,
	) (*mcplib.CallToolResult, error) {
		payload, err := topicPayload(req.GetArguments())
		if err != nil {
			return mcplib.NewToolResultError(err.Error()), nil
		}
		response, err := client.Post(ctx, "/v1/topic", payload)
		return toolResult(response, err)
	}
}

func makeIntelligenceHandler(
	client ServiceAPI,
	action string,
) server.ToolHandlerFunc {
	return func(
		ctx context.Context,
		req mcplib.CallToolRequest,
	) (*mcplib.CallToolResult, error) {
		payload, err := intelligencePayload(req.GetArguments(), action)
		if err != nil {
			return mcplib.NewToolResultError(err.Error()), nil
		}
		response, err := client.Post(ctx, "/v1/intelligence", payload)
		return toolResult(response, err)
	}
}

func makeServiceResourceHandler(
	client ServiceAPI,
	uri string,
	path string,
) server.ResourceHandlerFunc {
	return func(
		ctx context.Context,
		req mcplib.ReadResourceRequest,
	) ([]mcplib.ResourceContents, error) {
		if req.Params.URI != uri {
			return nil, errors.New("unknown last30days resource")
		}
		payload, err := client.Get(ctx, path)
		if err != nil {
			return nil, errors.New("last30days service info is unavailable")
		}
		return []mcplib.ResourceContents{
			mcplib.TextResourceContents{
				URI:      uri,
				MIMEType: "application/json",
				Text:     string(payload),
			},
		}, nil
	}
}

func queryPayload(args map[string]any, forceRefresh bool) (map[string]any, error) {
	query, err := requireString(args, "query", 4096)
	if err != nil {
		return nil, err
	}
	profileID := "default"
	if _, supplied := args["profile_id"]; supplied {
		profileID, err = requireString(args, "profile_id", 128)
		if err != nil {
			return nil, err
		}
	}
	if !profileIDPattern.MatchString(profileID) {
		return nil, errors.New("profile_id is invalid")
	}
	responseMode, err := enumArgument(
		args,
		"response_mode",
		"evidence",
		"evidence",
		"brief",
	)
	if err != nil {
		return nil, err
	}
	freshness := "force_refresh"
	if !forceRefresh {
		freshness, err = enumArgument(
			args,
			"freshness_policy",
			"prefer_cache",
			"prefer_cache",
			"cache_only",
			"refresh_if_stale",
		)
		if err != nil {
			return nil, err
		}
	}
	sources, err := stringArrayArgument(args, "sources", 32, 64)
	if err != nil {
		return nil, err
	}
	topicIDs, err := stringArrayArgument(args, "topic_ids", 32, 128)
	if err != nil {
		return nil, err
	}
	filters := map[string]any{}
	if len(sources) > 0 {
		filters["sources"] = sources
	}
	if len(topicIDs) > 0 {
		filters["topic_ids"] = topicIDs
	}
	for _, name := range []string{"published_after", "published_before"} {
		if value, ok, stringErr := optionalString(args, name, 64); stringErr != nil {
			return nil, stringErr
		} else if ok {
			filters[name] = value
		}
	}
	topK, err := integerArgument(args, "top_k", 8, 1, 100)
	if err != nil {
		return nil, err
	}
	maxChars, err := integerArgument(args, "max_chars", 8192, 512, 65536)
	if err != nil {
		return nil, err
	}
	payload := map[string]any{
		"schema_version":   servicecontracts.SchemaVersion,
		"profile_id":       profileID,
		"query":            query,
		"freshness_policy": freshness,
		"response_mode":    responseMode,
		"filters":          filters,
		"top_k":            topK,
		"max_chars":        maxChars,
		"wait_ms":          0,
	}
	payload["request_id"] = stableRequestID(payload)
	return payload, nil
}

func topicPayload(args map[string]any) (map[string]any, error) {
	action, err := enumArgument(
		args,
		"action",
		"",
		"list",
		"create",
		"update",
		"pause",
		"resume",
		"request_refresh",
	)
	if err != nil || action == "" {
		return nil, errors.New("action is required and must be supported")
	}
	payload := map[string]any{"action": action}
	for _, item := range []struct {
		name string
		max  int
	}{
		{"topic_id", 128},
		{"name", 256},
		{"schedule", 128},
	} {
		if value, ok, stringErr := optionalString(args, item.name, item.max); stringErr != nil {
			return nil, stringErr
		} else if ok {
			payload[item.name] = value
		}
	}
	for _, item := range []struct {
		name      string
		maxItems  int
		maxLength int
	}{
		{"search_queries", 32, 4096},
		{"sources", 32, 64},
	} {
		values, arrayErr := stringArrayArgument(
			args,
			item.name,
			item.maxItems,
			item.maxLength,
		)
		if arrayErr != nil {
			return nil, arrayErr
		}
		if len(values) > 0 {
			payload[item.name] = values
		}
	}
	return payload, nil
}

func intelligencePayload(args map[string]any, action string) (map[string]any, error) {
	payload := map[string]any{"action": action, "profile_id": "default"}
	if profileID, ok, err := optionalString(args, "profile_id", 128); err != nil {
		return nil, err
	} else if ok {
		payload["profile_id"] = profileID
	}
	switch action {
	case "temporal_query":
		query, err := requireString(args, "query", 4096)
		if err != nil {
			return nil, err
		}
		payload["query"] = query
		mode, err := enumArgument(
			args,
			"response_mode",
			"evidence",
			"evidence",
			"brief",
			"timeline",
			"entity_dossier",
			"event_dossier",
			"trend",
			"comparison",
		)
		if err != nil {
			return nil, err
		}
		payload["response_mode"] = mode
		for _, name := range []string{
			"as_of", "during_from", "during_to", "known_as_of",
		} {
			if value, ok, stringErr := optionalString(args, name, 64); stringErr != nil {
				return nil, stringErr
			} else if ok {
				payload[name] = value
			}
		}
		if _, fromOK := payload["during_from"]; fromOK {
			if _, toOK := payload["during_to"]; !toOK {
				return nil, errors.New("during_from and during_to must be supplied together")
			}
		} else if _, toOK := payload["during_to"]; toOK {
			return nil, errors.New("during_from and during_to must be supplied together")
		}
	case "profile_history":
		for _, item := range []struct {
			name string
			max  int
		}{
			{"source", 64},
			{"handle", 256},
		} {
			if value, ok, err := optionalString(args, item.name, item.max); err != nil {
				return nil, err
			} else if ok {
				payload[item.name] = value
			}
		}
		limit, err := integerArgument(args, "limit", 20, 1, 100)
		if err != nil {
			return nil, err
		}
		payload["limit"] = limit
	case "coverage", "maintenance_status":
		return payload, nil
	case "collection":
		operation, err := enumArgument(
			args, "operation", "", "list", "put", "pause", "resume", "run",
		)
		if err != nil || operation == "" {
			return nil, errors.New("operation is required and must be supported")
		}
		payload["operation"] = operation
		if spec, ok := args["spec"]; ok {
			mapping, valid := spec.(map[string]any)
			if !valid || len(mapping) > 32 {
				return nil, errors.New("spec must be a bounded object")
			}
			payload["spec"] = mapping
		}
		for _, item := range []struct {
			name string
			max  int
		}{
			{"collection_spec_id", 128},
			{"scheduled_for", 64},
		} {
			if value, ok, stringErr := optionalString(args, item.name, item.max); stringErr != nil {
				return nil, stringErr
			} else if ok {
				payload[item.name] = value
			}
		}
	default:
		return nil, errors.New("unsupported intelligence action")
	}
	return payload, nil
}

func optionalString(
	args map[string]any,
	name string,
	maximum int,
) (string, bool, error) {
	raw, ok := args[name]
	if !ok || raw == nil || raw == "" {
		return "", false, nil
	}
	value, ok := raw.(string)
	if !ok {
		return "", false, fmt.Errorf("%s must be a string", name)
	}
	value = strings.TrimSpace(value)
	if value == "" || len(value) > maximum {
		return "", false, fmt.Errorf("%s must be a bounded non-empty string", name)
	}
	return value, true, nil
}

func stableRequestID(payload map[string]any) string {
	encoded, _ := json.Marshal(payload)
	digest := sha256.Sum256(encoded)
	return "mcp-" + hex.EncodeToString(digest[:12])
}

func requireString(args map[string]any, name string, maximum int) (string, error) {
	raw, ok := args[name]
	if !ok {
		return "", fmt.Errorf("%s is required", name)
	}
	value, ok := raw.(string)
	value = strings.TrimSpace(value)
	if !ok || value == "" {
		return "", fmt.Errorf("%s must be a non-empty string", name)
	}
	if len(value) > maximum {
		return "", fmt.Errorf("%s cannot exceed %d characters", name, maximum)
	}
	return value, nil
}

func enumArgument(
	args map[string]any,
	name string,
	defaultValue string,
	allowed ...string,
) (string, error) {
	raw, ok := args[name]
	if !ok || raw == "" {
		return defaultValue, nil
	}
	value, ok := raw.(string)
	if !ok {
		return "", fmt.Errorf("%s must be a string", name)
	}
	for _, candidate := range allowed {
		if value == candidate {
			return value, nil
		}
	}
	return "", fmt.Errorf("%s is not supported", name)
}

func integerArgument(
	args map[string]any,
	name string,
	defaultValue, minimum, maximum int,
) (int, error) {
	raw, ok := args[name]
	if !ok {
		return defaultValue, nil
	}
	var value int
	switch typed := raw.(type) {
	case int:
		value = typed
	case float64:
		if typed != float64(int(typed)) {
			return 0, fmt.Errorf("%s must be an integer", name)
		}
		value = int(typed)
	default:
		return 0, fmt.Errorf("%s must be an integer", name)
	}
	if value < minimum || value > maximum {
		return 0, fmt.Errorf("%s must be between %d and %d", name, minimum, maximum)
	}
	return value, nil
}

func stringArrayArgument(
	args map[string]any,
	name string,
	maxItems, maxLength int,
) ([]string, error) {
	raw, ok := args[name]
	if !ok {
		return []string{}, nil
	}
	items, ok := raw.([]any)
	if !ok {
		if stringsValue, stringsOK := raw.([]string); stringsOK {
			items = make([]any, len(stringsValue))
			for index, value := range stringsValue {
				items[index] = value
			}
		} else {
			return nil, fmt.Errorf("%s must be an array of strings", name)
		}
	}
	if len(items) > maxItems {
		return nil, fmt.Errorf("%s cannot contain more than %d items", name, maxItems)
	}
	result := make([]string, 0, len(items))
	seen := make(map[string]struct{}, len(items))
	for _, rawItem := range items {
		item, ok := rawItem.(string)
		item = strings.TrimSpace(item)
		if !ok || item == "" || len(item) > maxLength {
			return nil, fmt.Errorf("%s must contain bounded non-empty strings", name)
		}
		if _, exists := seen[item]; exists {
			continue
		}
		seen[item] = struct{}{}
		result = append(result, item)
	}
	return result, nil
}

func toolResult(
	payload json.RawMessage,
	err error,
) (*mcplib.CallToolResult, error) {
	if err != nil {
		return mcplib.NewToolResultError(err.Error()), nil
	}
	return mcplib.NewToolResultText(string(payload)), nil
}
