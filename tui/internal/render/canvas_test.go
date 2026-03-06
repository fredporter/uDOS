package render

import (
	"regexp"
	"strings"
	"testing"

	"github.com/mattn/go-runewidth"
	"udos/tui/internal/protocol"
)

var ansiPattern = regexp.MustCompile(`\x1b\[[0-9;]*m`)

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

func TestRenderEventColumnsDoesNotOverflowCanvasWidth(t *testing.T) {
	theme := NewTheme()
	theme.CanvasWidth = 78
	maxRenderedWidth := theme.CanvasWidth + 2
	out := RenderEvent(theme, protocol.Event{
		Kind:  "columns",
		Title: "runner summary",
		Cols: []protocol.Column{
			{Title: "status", Lines: []string{"job: sonic.status", "state: request run-123 accepted"}},
			{Title: "recent", Lines: []string{"LOG: Local operator guidance ready", "BLOCK: OUTPUT"}},
		},
	})
	for _, line := range strings.Split(out, "\n") {
		clean := ansiPattern.ReplaceAllString(line, "")
		if runewidth.StringWidth(clean) > maxRenderedWidth {
			t.Fatalf("line width overflow: got=%d want<=%d line=%q", runewidth.StringWidth(clean), maxRenderedWidth, clean)
		}
	}
}
