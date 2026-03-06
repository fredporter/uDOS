package app

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"

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
		askInput:   primitives.NewInput("FREEFORM QUESTION", "Ask a question", 72, nil),
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

func TestHomeNumericShortcutOpensCustomCommandMode(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("9")})
	updated := next.(Model)
	if updated.mode != modeInput {
		t.Fatalf("expected modeInput, got %s", updated.mode)
	}
}

func TestHomeQuestionMarkOpensFreeformPromptMode(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("?")})
	updated := next.(Model)
	if updated.mode != modeAsk {
		t.Fatalf("expected modeAsk, got %s", updated.mode)
	}
}

func TestAskModeEnterBuildsOkAskCommand(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("?")})
	updated := next.(Model)
	updated.askInput.Model.SetValue("how is health status")
	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated = next.(Model)
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastJob != "ucode.command" {
		t.Fatalf("expected lastJob ucode.command, got %s", updated.lastJob)
	}
	if updated.lastCommand != "OK ASK how is health status" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestQuestionMarkFromRunnerOpensFreeformPromptMode(t *testing.T) {
	m := newTestModel(t)
	m.mode = modeRunner
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("?")})
	updated := next.(Model)
	if updated.mode != modeAsk {
		t.Fatalf("expected modeAsk, got %s", updated.mode)
	}
}

func TestQuestionMarkInAskModeUpdatesInput(t *testing.T) {
	m := newTestModel(t)
	m.mode = modeAsk
	m.askInput.Focus()
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("?")})
	updated := next.(Model)
	if updated.askInput.Value() != "?" {
		t.Fatalf("expected ask input to capture '?', got %q", updated.askInput.Value())
	}
}

func TestF1TogglesHelpFlag(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyF1})
	updated := next.(Model)
	if !updated.showHelp {
		t.Fatalf("expected showHelp true after first F1")
	}
	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyF1})
	updated = next.(Model)
	if updated.showHelp {
		t.Fatalf("expected showHelp false after second F1")
	}
}

func TestRunnerEnterReturnsHome(t *testing.T) {
	m := newTestModel(t)
	m.mode = modeRunner
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	updated := next.(Model)
	if updated.mode != modeHome {
		t.Fatalf("expected modeHome, got %s", updated.mode)
	}
}

func TestRunSelectionCommandPrefixStartsUcodeCommandJob(t *testing.T) {
	m := newTestModel(t)
	selected := primitives.MenuItem{
		Key:   "s",
		Label: "Startup Script",
		Desc:  "Run startup script",
		Value: "ucode.command:RUN memory/bank/system/startup-script.md",
	}
	next, _ := m.runSelection(selected)
	updated, ok := next.(Model)
	if !ok {
		t.Fatalf("expected model type")
	}
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastJob != "ucode.command" {
		t.Fatalf("expected lastJob ucode.command, got %s", updated.lastJob)
	}
	if updated.lastCommand != "RUN memory/bank/system/startup-script.md" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestMenuColumnCountThresholds(t *testing.T) {
	tests := []struct {
		width int
		want  int
	}{
		{width: 60, want: 1},
		{width: 70, want: 2},
		{width: 80, want: 2},
		{width: 109, want: 2},
		{width: 110, want: 3},
		{width: 140, want: 3},
	}
	for _, tc := range tests {
		got := menuColumnCount(tc.width)
		if got != tc.want {
			t.Fatalf("menuColumnCount(%d) = %d, want %d", tc.width, got, tc.want)
		}
	}
}

func TestRunnerColumnCountThresholds(t *testing.T) {
	tests := []struct {
		width int
		want  int
	}{
		{width: 69, want: 1},
		{width: 78, want: 2},
		{width: 100, want: 2},
		{width: 119, want: 2},
		{width: 120, want: 3},
	}
	for _, tc := range tests {
		got := runnerColumnCount(tc.width)
		if got != tc.want {
			t.Fatalf("runnerColumnCount(%d) = %d, want %d", tc.width, got, tc.want)
		}
	}
}

func TestHomeArrowNavigationFollowsVisualColumns(t *testing.T) {
	m := newTestModel(t)
	m.theme.CanvasWidth = 80 // 2-column menu in current thresholds
	m.selectOne.List.Select(0)

	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyDown})
	updated := next.(Model)
	if updated.selectOne.List.Index() != 2 {
		t.Fatalf("down should move to next visual row in same column, got index %d", updated.selectOne.List.Index())
	}

	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyRight})
	updated = next.(Model)
	if updated.selectOne.List.Index() != 3 {
		t.Fatalf("right should move to adjacent column, got index %d", updated.selectOne.List.Index())
	}

	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyUp})
	updated = next.(Model)
	if updated.selectOne.List.Index() != 1 {
		t.Fatalf("up should move to previous visual row, got index %d", updated.selectOne.List.Index())
	}

	next, _ = updated.Update(tea.KeyMsg{Type: tea.KeyLeft})
	updated = next.(Model)
	if updated.selectOne.List.Index() != 0 {
		t.Fatalf("left should move to previous column, got index %d", updated.selectOne.List.Index())
	}
}

func TestRenderHomeMenuIncludesPredictiveCommandBlock(t *testing.T) {
	m := newTestModel(t)
	m.theme.CanvasWidth = 80
	view := m.renderHomeMenu()
	if !strings.Contains(view, "PREDICTIVE COMMAND") {
		t.Fatalf("expected predictive command block in home menu")
	}
}
