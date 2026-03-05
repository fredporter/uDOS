package app

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/viewport"

	"udos/tui/internal/backend"
	"udos/tui/internal/primitives"
	"udos/tui/internal/protocol"
	"udos/tui/internal/render"
)

type screenMode string

const (
	modeHome   screenMode = "home"
	modeInput  screenMode = "input"
	modePath   screenMode = "path"
	modeRunner screenMode = "runner"
)

type backendMessage struct {
	msg protocol.Message
	err error
}

type Model struct {
	theme        render.Theme
	mode         screenMode
	width        int
	height       int
	selectOne    primitives.SelectOne
	input        primitives.Input
	pathPicker   primitives.PickerPath
	pathInput    primitives.Input
	viewport     viewport.Model
	help         help.Model
	spinner      spinner.Model
	backend      *backend.Client
	events       []protocol.Event
	showHelp     bool
	statusLine   string
	lastError    string
	currentJobID string
	lastJob      string
	lastCommand  string
}

func actionItems() []primitives.MenuItem {
	return []primitives.MenuItem{
		{Key: "0", Label: "Pick Path", Desc: "Pick an existing path and inspect it", Value: "picker.path"},
		{Key: "1", Label: "Status", Desc: "System status and route health", Value: "status"},
		{Key: "2", Label: "Workflow Templates", Desc: "List workflow templates", Value: "workflow.templates"},
		{Key: "3", Label: "Workflow Runs", Desc: "List workflow runs", Value: "workflow.runs"},
		{Key: "4", Label: "Knowledge Templates", Desc: "List template families", Value: "knowledge.templates"},
		{Key: "5", Label: "Research Notes", Desc: "List persisted research notes", Value: "knowledge.research.list"},
		{Key: "6", Label: "Health", Desc: "Run runtime health checks", Value: "health.status"},
		{Key: "7", Label: "Repair Status", Desc: "Show Python and runtime status", Value: "repair.status"},
		{Key: "8", Label: "Sonic Status", Desc: "Show Sonic runtime status", Value: "sonic.status"},
		{Key: "9", Label: "Custom Command", Desc: "Enter a full ucode command", Value: "custom.command"},
	}
}

func NewModel() (Model, error) {
	repoRoot, err := os.Getwd()
	if err != nil {
		return Model{}, err
	}
	repoRoot, err = filepath.Abs(repoRoot)
	if err != nil {
		return Model{}, err
	}
	client, err := backend.Start(repoRoot)
	if err != nil {
		return Model{}, err
	}
	selectOne := primitives.NewSelectOne("uDOS v1.5", actionItems(), 78, 12, true)
	input := primitives.NewInput("CUSTOM COMMAND", "Enter ucode command", 72, nil)
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
				return fmt.Errorf("path is required")
			}
			if pathPicker.MustExist {
				if _, err := os.Stat(value); err != nil {
					return fmt.Errorf("path does not exist")
				}
			}
			return nil
		},
	)

	vp := viewport.New(78, 18)
	vp.SetContent("")

	spin := spinner.New()
	spin.Spinner = spinner.Line

	return Model{
		theme:    render.NewTheme(),
		mode:     modeHome,
		selectOne: selectOne,
		input:    input,
		pathPicker: pathPicker,
		pathInput:  pathInput,
		viewport: vp,
		help:     help.New(),
		spinner:  spin,
		backend:  client,
	}, nil
}

func waitForBackend(client *backend.Client) tea.Cmd {
	return func() tea.Msg {
		select {
		case msg := <-client.Messages():
			return backendMessage{msg: msg}
		case err := <-client.Errors():
			return backendMessage{err: err}
		}
	}
}

func (m Model) Init() tea.Cmd {
	return tea.Batch(
		m.spinner.Tick,
		sendHello(m.backend, m.theme.CanvasWidth),
		waitForBackend(m.backend),
	)
}

func sendHello(client *backend.Client, width int) tea.Cmd {
	hello := protocol.Message{
		V:      1,
		Type:   "hello",
		ID:     backend.RequestID("hello"),
		Client: &protocol.ClientInfo{Name: "udos-tui", Version: "0.2.0"},
		Caps: &protocol.ClientCaps{
			TTY:   true,
			Width: width,
			Color: "256",
			Paste: "bracketed",
		},
	}
	return func() tea.Msg {
		_ = client.Send(hello)
		return nil
	}
}

func sanitizeSingleLineInput(raw string) string {
	if raw == "" {
		return ""
	}
	s := strings.ReplaceAll(raw, "\x00", "")
	s = strings.ReplaceAll(s, "\r\n", " ")
	s = strings.ReplaceAll(s, "\n", " ")
	s = strings.ReplaceAll(s, "\r", " ")
	return strings.TrimSpace(s)
}

func (m Model) cycleMode(forward bool) Model {
	seq := []screenMode{modeHome, modeInput, modePath, modeRunner}
	idx := 0
	for i, mode := range seq {
		if mode == m.mode {
			idx = i
			break
		}
	}
	if forward {
		idx = (idx + 1) % len(seq)
	} else {
		idx = (idx + len(seq) - 1) % len(seq)
	}
	next := seq[idx]
	m.mode = next
	if next == modeInput {
		m.input.Focus()
		m.pathInput.Blur()
	} else if next == modePath {
		m.pathInput.Focus()
		m.input.Blur()
	} else {
		m.input.Blur()
		m.pathInput.Blur()
	}
	return m
}

func (m Model) reloadCurrent() (tea.Model, tea.Cmd) {
	if m.lastJob != "" {
		return m.startJob(m.lastJob, m.lastCommand)
	}
	m.statusLine = "refreshing backend metadata"
	return m, tea.Batch(
		sendHello(m.backend, m.theme.CanvasWidth),
		waitForBackend(m.backend),
	)
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.selectOne.List.SetWidth(max(20, msg.Width-2))
		m.viewport.Width = max(20, min(msg.Width-2, m.theme.CanvasWidth))
		m.viewport.Height = max(8, msg.Height-8)
		return m, nil
	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	case backendMessage:
		if msg.err != nil {
			m.lastError = msg.err.Error()
			return m, waitForBackend(m.backend)
		}
		if msg.msg.Type == "result" {
			m.statusLine = fmt.Sprintf("request %s accepted", msg.msg.ID)
			if value, ok := msg.msg.Value.(map[string]interface{}); ok {
				if status, ok := value["status"].(string); ok && status == "ready" {
					m.statusLine = "backend ready"
					if actions, ok := value["actions"].([]interface{}); ok {
						m.selectOne.List.SetItems(actionsToListItems(actions))
					}
				}
				if jobID, ok := value["job_id"].(string); ok {
					m.currentJobID = jobID
				}
			}
		}
		if msg.msg.Type == "event" && msg.msg.Event != nil {
			m.events = append(m.events, *msg.msg.Event)
			m.viewport.SetContent(m.renderEvents())
		}
		if msg.msg.Type == "done" {
			if msg.msg.OK {
				m.statusLine = fmt.Sprintf("job %s finished", msg.msg.ID)
			} else {
				m.statusLine = fmt.Sprintf("job %s failed", msg.msg.ID)
				if msg.msg.Error != "" {
					m.lastError = msg.msg.Error
				}
			}
		}
		return m, waitForBackend(m.backend)
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "ctrl+r":
			return m.reloadCurrent()
		case "?":
			m.showHelp = !m.showHelp
			return m, nil
		case "m":
			m.theme.TeletextUnicode = !m.theme.TeletextUnicode
			if m.theme.TeletextUnicode {
				m.statusLine = "teletext mode: unicode blocks"
			} else {
				m.statusLine = "teletext mode: ascii"
			}
			m.viewport.SetContent(m.renderEvents())
			return m, nil
		case "ctrl+l":
			return m, tea.ClearScreen
		case "tab":
			m = m.cycleMode(true)
			return m, nil
		case "shift+tab":
			m = m.cycleMode(false)
			return m, nil
		case "esc":
			if m.mode == modeRunner || m.mode == modeInput || m.mode == modePath {
				m.mode = modeHome
				return m, nil
			}
		}

		switch m.mode {
		case modeHome:
			if msg.String() == "n" {
				msg = tea.KeyMsg{Type: tea.KeyDown}
			} else if msg.String() == "N" {
				msg = tea.KeyMsg{Type: tea.KeyUp}
			}
			if msg.String() == "enter" {
				selected, ok := m.selectOne.Selected()
				if !ok {
					return m, nil
				}
				if selected.Value == "picker.path" {
					m.mode = modePath
					m.pathInput.Focus()
					if m.pathInput.Value() == "" {
						m.pathInput.Model.SetValue(m.pathPicker.StartDir)
					}
					return m, nil
				}
				if selected.Value == "custom.command" {
					m.mode = modeInput
					m.input.Focus()
					return m, nil
				}
				return m.startJob(selected.Value, "")
			}
			var cmd tea.Cmd
			m.selectOne, cmd = m.selectOne.Update(msg)
			return m, cmd
		case modeInput:
			if msg.String() == "enter" {
				command := sanitizeSingleLineInput(m.input.Value())
				if command == "" {
					return m, nil
				}
				m.input.Blur()
				return m.startJob("ucode.command", command)
			}
			var cmd tea.Cmd
			m.input, cmd = m.input.Update(msg)
			return m, cmd
		case modePath:
			if msg.String() == "enter" {
				if !m.pathInput.Validate() {
					return m, nil
				}
				command := fmt.Sprintf("READ %s", strings.TrimSpace(m.pathInput.Value()))
				m.pathInput.Blur()
				return m.startJob("ucode.command", command)
			}
			var cmd tea.Cmd
			m.pathInput, cmd = m.pathInput.Update(msg)
			return m, cmd
		case modeRunner:
			var cmd tea.Cmd
			m.viewport, cmd = m.viewport.Update(msg)
			return m, cmd
		}
	}
	return m, nil
}

func (m Model) startJob(job, command string) (tea.Model, tea.Cmd) {
	m.mode = modeRunner
	m.events = nil
	m.lastError = ""
	m.statusLine = "running"
	m.lastJob = job
	m.lastCommand = command
	m.viewport.SetContent("")
	req := protocol.Message{
		V:    1,
		Type: "run",
		ID:   backend.RequestID("run"),
		Job:  job,
	}
	if command != "" {
		req.Args = protocol.RunArgs{Command: command}
	}
	return m, tea.Batch(
		func() tea.Msg {
			_ = m.backend.Send(req)
			return nil
		},
		waitForBackend(m.backend),
	)
}

func (m Model) View() string {
	header := render.RenderHeader(
		m.theme,
		"uDOS v1.5 teletext shell",
		"Bubble Tea + Lip Gloss frontend over the v1.5 JSONL runtime contract",
	)
	body := ""
	switch m.mode {
	case modeHome:
		body = m.selectOne.View()
	case modeInput:
		body = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "CUSTOM COMMAND",
				Style: "accent",
				Lines: []string{m.input.View()},
			},
		)
	case modePath:
		body = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "PICK PATH",
				Style: "accent",
				Lines: []string{
					"Provide a path, then press Enter to run READ <path>",
					m.pathInput.View(),
				},
			},
		)
	case modeRunner:
		body = m.viewport.View()
	}
	footer := "Enter select  / filter  n next  N prev  m teletext  Tab next  Shift+Tab prev  Esc back  Ctrl+R refresh  ? help  Ctrl+L redraw  Ctrl+C quit"
	if m.statusLine != "" {
		footer = footer + " | " + m.statusLine
	}
	if m.lastError != "" {
		footer = footer + " | error: " + m.lastError
	}
	return strings.Join([]string{
		header,
		body,
		m.theme.Footer.Width(m.theme.CanvasWidth).Render(footer),
	}, "\n\n")
}

func (m Model) renderEvents() string {
	rendered := make([]string, 0, len(m.events))
	for _, event := range m.events {
		rendered = append(rendered, render.RenderEvent(m.theme, event))
	}
	return strings.Join(rendered, "\n\n")
}

func actionsToListItems(raw []interface{}) []list.Item {
	items := make([]list.Item, 0, len(raw))
	for _, entry := range raw {
		action, ok := entry.(map[string]interface{})
		if !ok {
			continue
		}
		key, _ := action["key"].(string)
		label, _ := action["label"].(string)
		job, _ := action["job"].(string)
		items = append(items, primitives.MenuItem{
			Key:   key,
			Label: label,
			Desc:  fmt.Sprintf("Run %s", job),
			Value: job,
		})
	}
	if len(items) == 0 {
		defaults := actionItems()
		fallback := make([]list.Item, 0, len(defaults))
		for _, item := range defaults {
			fallback = append(fallback, item)
		}
		return fallback
	}
	return items
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
