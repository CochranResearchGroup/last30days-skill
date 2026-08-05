package contracts

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestGeneratedCatalogIsCurrent(t *testing.T) {
	path := filepath.Join(
		"..", "..", "..",
		"skills", "last30days", "schemas", "service-contracts-v1.json",
	)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	digest := sha256.Sum256(raw)
	if got := hex.EncodeToString(digest[:]); got != CatalogSHA256 {
		t.Fatalf(
			"generated contract catalog is stale: got %s, want %s; run go generate ./internal/contracts",
			CatalogSHA256,
			got,
		)
	}
	wantRequest := []string{
		"filters", "freshness_policy", "max_chars", "profile_id", "query",
		"request_id", "response_mode", "schema_version", "top_k", "wait_ms",
	}
	wantFilters := []string{
		"published_after", "published_before", "sources", "topic_ids",
	}
	if !reflect.DeepEqual(QueryRequestFields, wantRequest) {
		t.Fatalf("query request fields drifted: %#v", QueryRequestFields)
	}
	if !reflect.DeepEqual(QueryFilterFields, wantFilters) {
		t.Fatalf("query filter fields drifted: %#v", QueryFilterFields)
	}
	if ProductIdentity != "last30days" ||
		ServiceAPIMin != 1 ||
		ServiceAPIMax != 1 ||
		DatabaseSchemaMin != 14 ||
		DatabaseSchemaMax != 14 {
		t.Fatal("generated compatibility facts drifted")
	}
}
