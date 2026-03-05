package render

import (
	"strings"
	"testing"

	"udos/tui/internal/protocol"
)

func TestRenderEventLogKind(t *testing.T) {
	theme := NewTheme()
	out := RenderEvent(theme, protocol.Event{
		Kind:    "log",
		Level:   "warn",
		Message: "missing config",
		Fields: map[string]string{
			"path": "core/config.toml",
		},
	})
	if !strings.Contains(out, "LOG") {
		t.Fatalf("expected LOG title in output: %q", out)
	}
	if !strings.Contains(out, "[WARN] missing config") {
		t.Fatalf("expected warn line in output: %q", out)
	}
	if !strings.Contains(out, "path=core/config.toml") {
		t.Fatalf("expected fields line in output: %q", out)
	}
}

func TestRenderEventRuleKind(t *testing.T) {
	theme := NewTheme()
	out := RenderEvent(theme, protocol.Event{Kind: "rule"})
	if !strings.Contains(out, strings.Repeat("-", theme.CanvasWidth)) {
		t.Fatalf("expected full-width divider in output: %q", out)
	}
}

func TestRenderEventColumnsKind(t *testing.T) {
	theme := NewTheme()
	out := RenderEvent(theme, protocol.Event{
		Kind:  "columns",
		Title: "overview",
		Cols: []protocol.Column{
			{Title: "left", Lines: []string{"a", "b"}},
			{Title: "right", Lines: []string{"c", "d"}},
		},
	})
	if !strings.Contains(out, "OVERVIEW") {
		t.Fatalf("expected columns title in output: %q", out)
	}
	if !strings.Contains(out, "LEFT") || !strings.Contains(out, "RIGHT") {
		t.Fatalf("expected column headers in output: %q", out)
	}
}
