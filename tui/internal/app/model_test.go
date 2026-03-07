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

func TestHomeEnterRunsFirstStartupCommand(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyEnter})
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
	if updated.lastCommand != "BINDER CREATE @binder/new-mission" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestRunSelectionPathModeRejectsMissingPath(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.runSelection(primitives.MenuItem{Value: "picker.path"})
	updated, ok := next.(Model)
	if !ok {
		t.Fatalf("expected model type")
	}

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

func TestRunSelectionPathModeBuildsReadCommandForExistingPath(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.runSelection(primitives.MenuItem{Value: "picker.path"})
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
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastCommand != "MODE THEME LIST" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestHomeWizardShortcutRunsWizardStart(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("w"), Alt: true})
	updated := next.(Model)
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastCommand != "WIZARD START" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestHomeDevShortcutRunsDevPlan(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("d"), Alt: true})
	updated := next.(Model)
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastCommand != "DEV PLAN" {
		t.Fatalf("unexpected lastCommand: %s", updated.lastCommand)
	}
}

func TestHomeSlashOpensCommandMode(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("/")})
	updated := next.(Model)
	if updated.mode != modeInput {
		t.Fatalf("expected modeInput, got %s", updated.mode)
	}
	if updated.input.Value() != "/" {
		t.Fatalf("expected input to be prefilled with '/', got %q", updated.input.Value())
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

func TestAskModeCtrlMBuildsOkAskCommand(t *testing.T) {
	m := newTestModel(t)
	m.mode = modeAsk
	m.askInput.Focus()
	m.askInput.Model.SetValue("status please")
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlM})
	updated := next.(Model)
	if updated.mode != modeRunner {
		t.Fatalf("expected modeRunner, got %s", updated.mode)
	}
	if updated.lastCommand != "OK ASK status please" {
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

func TestRunSelectionFreeformAskOpensAskMode(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.runSelection(primitives.MenuItem{Value: "freeform.ask"})
	updated := next.(Model)
	if updated.mode != modeAsk {
		t.Fatalf("expected modeAsk, got %s", updated.mode)
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

func TestHelpPanelIncludesShellAndTUISkillExamples(t *testing.T) {
	m := newTestModel(t)
	m.showHelp = true
	view := m.View()
	if !strings.Contains(view, "ucode status @workspace --option") {
		t.Fatalf("expected shell help example in help panel")
	}
	if !strings.Contains(view, "run @user/sandbox/demo-script.md --fullscreen") {
		t.Fatalf("expected run help example in help panel")
	}
}

func TestInputAutocompleteAcceptsWithRightArrow(t *testing.T) {
	m := newTestModel(t)
	m.mode = modeInput
	m.input.Focus()
	m.input.Model.SetValue("sta")
	next, _ := m.Update(tea.KeyMsg{Type: tea.KeyRight})
	updated := next.(Model)
	if updated.input.Value() == "sta" {
		t.Fatalf("expected right arrow to accept completion")
	}
	if !strings.HasPrefix(strings.ToLower(updated.input.Value()), "status") {
		t.Fatalf("expected status completion, got %q", updated.input.Value())
	}
}

func TestInputSuggestionsIncludeWorkspaceRefsAndOptions(t *testing.T) {
	m := newTestModel(t)
	m.workspaceRefs = []string{"@workspace", "@binder"}
	at := m.inputSuggestions("status @wo")
	if len(at) == 0 || !strings.Contains(strings.ToLower(strings.Join(at, " ")), "@workspace") {
		t.Fatalf("expected @workspace suggestion, got %v", at)
	}

	opts := m.inputSuggestions("status --co")
	if len(opts) == 0 {
		t.Fatalf("expected option suggestions, got none")
	}
	joined := strings.ToLower(strings.Join(opts, " "))
	if !strings.Contains(joined, "--compact") {
		t.Fatalf("expected --compact suggestion, got %v", opts)
	}
}

func TestAllStartupMenuOptionsHaveRunnableRoutes(t *testing.T) {
	m := newTestModel(t)
	for _, item := range actionItems() {
		next, _ := m.runSelection(item)
		updated, ok := next.(Model)
		if !ok {
			t.Fatalf("expected model type for key %q", item.Key)
		}
		switch {
		case item.Value == "freeform.ask":
			if updated.mode != modeAsk {
				t.Fatalf("key %q expected modeAsk, got %s", item.Key, updated.mode)
			}
		case strings.HasPrefix(item.Value, "ucode.command:"):
			if updated.mode != modeRunner {
				t.Fatalf("key %q expected modeRunner, got %s", item.Key, updated.mode)
			}
			want := strings.TrimPrefix(item.Value, "ucode.command:")
			if updated.lastCommand != want {
				t.Fatalf("key %q expected command %q, got %q", item.Key, want, updated.lastCommand)
			}
		default:
			t.Fatalf("key %q has unsupported route value %q", item.Key, item.Value)
		}
	}
}

func TestActionsToListItemsPrefersCommandWhenPresent(t *testing.T) {
	items := actionsToListItems(
		[]interface{}{
			map[string]interface{}{
				"key":     "x",
				"label":   "Guided Status",
				"job":     "ucode.command",
				"command": "STATUS",
			},
		},
		nil,
	)
	if len(items) != 1 {
		t.Fatalf("expected one item, got %d", len(items))
	}
	menu, ok := items[0].(primitives.MenuItem)
	if !ok {
		t.Fatalf("expected primitives.MenuItem type")
	}
	if menu.Value != "ucode.command:STATUS" {
		t.Fatalf("expected value to include command route, got %q", menu.Value)
	}
}

func TestWindowResizeUsesRenderedChromeForViewportHeight(t *testing.T) {
	m := newTestModel(t)
	next, _ := m.Update(tea.WindowSizeMsg{Width: 100, Height: 30})
	updated := next.(Model)

	header := render.RenderHeader(
		updated.theme,
		"uDOS v1.5 teletext shell",
		"Bubble Tea + Lip Gloss | v1.5 JSONL runtime",
	)
	footer := updated.renderFooter()
	expected := 30 - (strings.Count(header, "\n") + 1) - (strings.Count(footer, "\n") + 1) - 4
	if expected < 6 {
		expected = 6
	}
	if updated.viewport.Height != expected {
		t.Fatalf("viewport height=%d, want %d", updated.viewport.Height, expected)
	}
}
