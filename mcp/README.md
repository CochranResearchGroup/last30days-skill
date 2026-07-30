# Last30Days MCP adapter

CGO-free Go MCP server that connects Claude Desktop and other MCP hosts to the
user-scoped last30days intelligence service over its private Unix socket.

The adapter exposes:

- `service_info`
- `query` (`prefer_cache` by default; `cache_only` prohibits external work)
- `refresh` (`force_refresh`, durable and idempotent)
- `job_status`
- `topic`
- resources `last30days://capabilities`, `last30days://sources`, and
  `last30days://topics`

It contains no acquisition logic. The bundle carries the independently
versioned service artifact and its managed user-service installer. When no
service is running, bootstrap installs and starts that artifact through the
managed lifecycle; it does not detach `service.py` or become the daemon owner.
An MCP query never starts a request-scoped research engine, browser, or
scraper.

## Layout

- `cmd/last30days-pp-mcp/` - stdio entry point
- `internal/service/` - bounded HTTP client over the Unix socket
- `internal/tools/` - MCP tools, resource, schemas, annotations, and handlers
- `internal/manifest/` - MCPB manifest validation
- `internal/contracts/` - generated compatibility facts from the canonical
  JSON Schema catalog
- `internal/engine/` - unlinked legacy source retained temporarily for history
  and release-script migration; it is not reachable from the registered binary

## Development

```bash
go test ./...
go vet ./...
go generate ./internal/contracts
go build ./cmd/last30days-pp-mcp
go list -deps ./cmd/last30days-pp-mcp | grep internal/engine
```

The last command must return no dependency.

## Runtime

The MCPB can bootstrap its packaged service artifact automatically through the
same managed installer used for explicit lifecycle operations. Operators may
instead build and install the user service explicitly:

```bash
bash ../service/scripts/build-runtime.sh
bash ../service/scripts/install.sh install \
  --artifact ../dist/service/last30days-service-0.2.7.tar.gz
bash ../service/scripts/install.sh status
```

Socket resolution matches the Python service:

1. `LAST30DAYS_SERVICE_SOCKET`
2. `$XDG_RUNTIME_DIR/last30days/service.sock`
3. `/run/user/<uid>/last30days/service.sock`

The MCPB manifest accepts only the optional socket override. Source
credentials stay in the service's user-scoped configuration; they are never
injected into the MCP process.

The v4 adapter is Linux-only until macOS and Windows have an equivalent
owner-private managed-service bootstrap.
