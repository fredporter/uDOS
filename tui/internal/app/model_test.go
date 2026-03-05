package app

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/viewport"

	"udos/tui/internal/primitives"
	"udos/tui/internal/render"
)

func newTestModel(t *testing.T) Model {
	t.Helper()
	selectOne := primitives.NewSelectOne("uDOS v1.5", actionItems(), 78, 12, true)
	pathPicker := primitives.PickerPath{
		Title:     "Pick Path",
		StartDir:  ".",
		MustExist: true,
	}
	pathInput := primitives.NewInput(
		"PICK PATH",
		"Enter file or folder path",
		72,
		func(value string) error {
			if strings.TrimSpace(value) == "" {
				return os.ErrInvalid
			}
			if _, err := os.Stat(value); err != nil {
				return err
			}
			return nil
		},
	)
	vp := viewport.New(78, 18)
	spin := spinner.New()
	spin.Spinner = spinner.Line
	return Model{
		theme:      render.NewTheme(),
		mode:       modeHome,
		selectOne:  selectOne,
		input:      primitives.NewInput("CUSTOM COMMAND", "Enter ucode command", 72, nil),
		pathPicker: pathPicker,
		pathInput:  pathInput,
		viewport:   vp,
		help:       help.New(),
		spinner:    spin,
	}
}

func TestHomePickerPathSelectionEntersPathMode(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated, ok := next.(Model)
	if !ok {
		t.Fatalf("expected model type")
	}
	if updated.mode != modePath {
		t.Fatalf("expected modePath, got %s", updated.mode)
	}
}

func TestPathModeRejectsMissingPath(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated := next.(Model)

	updated.pathInput.Model.SetValue("/tmp/does-not-exist-udos-test")
	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated = next.(Model)

	if updated.mode != modePath {
		t.Fatalf("expected to remain in modePath, got %s", updated.mode)
	}
	if updated.pathInput.Error == "" {
		t.Fatalf("expected validation error for missing path")
	}
}

func TestPathModeBuildsReadCommandForExistingPath(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated := next.(Model)

	tempDir := t.TempDir()
	filePath := filepath.Join(tempDir, "sample.txt")
	if err := os.WriteFile(filePath, []byte("hello"), 0o644); err != nil {
		t.Fatalf("write file: %v", err)
	}

	updated.pathInput.Model.SetValue(filePath)
	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated = next.(Model)

	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	want := "READ " + filePath
	if updated.lastCommand != want {
		t.Fatalf("expected lastCommand %q, got %q", want, updated.lastCommand)
	}
}
