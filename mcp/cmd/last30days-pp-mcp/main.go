// Package main is the stdio MCP adapter for the local last30days service.
package main

import (
	"fmt"
	"os"

	"github.com/mark3labs/mcp-go/server"

	"github.com/mvanhorn/last30days-skill/mcp/internal/tools"
)

// Version is stamped at build time via -ldflags "-X main.Version=<tag>".
var Version = "dev"

const (
	serverName    = "last30days"
	serverVersion = "1"
)

func main() {
	s := server.NewMCPServer(
		serverName,
		serverVersion,
		server.WithToolCapabilities(false),
		server.WithResourceCapabilities(false, false),
	)

	tools.Register(s, tools.Config{})

	if err := server.ServeStdio(s); err != nil {
		fmt.Fprintf(os.Stderr, "last30days-pp-mcp: %v\n", err)
		os.Exit(1)
	}
}
