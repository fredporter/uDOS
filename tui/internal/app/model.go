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
	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"

	"udos/tui/internal/backend"
	"udos/tui/internal/protocol"
	"udos/tui/internal/render"
)

type screenMode string

const (
	modeHome   screenMode = "home"
	modeInput  screenMode = "input"
	modeRunner screenMode = "runner"
)

type actionItem struct {
	title string
	desc  string
	job   string
}

func (i actionItem) Title() string       { return i.title }
func (i actionItem) Description() string { return i.desc }
func (i actionItem) FilterValue() string { return i.title + " " + i.desc }

type backendMessage struct {
	msg protocol.Message
	err error
}

type Model struct {
	theme        render.Theme
	mode         screenMode
	width        int
	height       int
	list         list.Model
	input        textinput.Model
	viewport     viewport.Model
	help         help.Model
	spinner      spinner.Model
	backend      *backend.Client
	events       []protocol.Event
	showHelp     bool
	statusLine   string
	lastError    string
	currentJobID string
}

func actionItems() []list.Item {
	return []list.Item{
		actionItem{title: "1. Status", desc: "System status and route health", job: "status"},
		actionItem{title: "2. Workflow Templates", desc: "List workflow templates", job: "workflow.templates"},
		actionItem{title: "3. Workflow Runs", desc: "List workflow runs", job: "workflow.runs"},
		actionItem{title: "4. Knowledge Templates", desc: "List template families", job: "knowledge.templates"},
		actionItem{title: "5. Research Notes", desc: "List persisted research notes", job: "knowledge.research.list"},
		actionItem{title: "6. Health", desc: "Run runtime health checks", job: "health.status"},
		actionItem{title: "7. Repair Status", desc: "Show Python and runtime status", job: "repair.status"},
		actionItem{title: "8. Sonic Status", desc: "Show Sonic runtime status", job: "sonic.status"},
		actionItem{title: "9. Custom Command", desc: "Enter a full ucode command", job: "custom.command"},
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
	l := list.New(actionItems(), list.NewDefaultDelegate(), 78, 12)
	l.Title = "uDOS v1.5"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)

	ti := textinput.New()
	ti.Placeholder = "Enter ucode command"
	ti.CharLimit = 512
	ti.Width = 72

	vp := viewport.New(78, 18)
	vp.SetContent("")

	spin := spinner.New()
	spin.Spinner = spinner.Line

	return Model{
		theme:    render.NewTheme(),
		mode:     modeHome,
		list:     l,
		input:    ti,
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
	hello := protocol.Message{
		V:    1,
		Type: "hello",
		ID:   backend.RequestID("hello"),
	}
	return tea.Batch(
		m.spinner.Tick,
		func() tea.Msg {
			_ = m.backend.Send(hello)
			return nil
		},
		waitForBackend(m.backend),
	)
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.list.SetWidth(msg.Width - 2)
		m.viewport.Width = min(msg.Width-2, m.theme.CanvasWidth)
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
			m.statusLine = fmt.Sprintf("job %s finished", msg.msg.ID)
		}
		return m, waitForBackend(m.backend)
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "?":
			m.showHelp = !m.showHelp
			return m, nil
		case "ctrl+l":
			return m, tea.ClearScreen
		case "esc":
			if m.mode == modeRunner || m.mode == modeInput {
				m.mode = modeHome
				return m, nil
			}
		}

		switch m.mode {
		case modeHome:
			if msg.String() == "enter" {
				selected, ok := m.list.SelectedItem().(actionItem)
				if !ok {
					return m, nil
				}
				if selected.job == "custom.command" {
					m.mode = modeInput
					m.input.Focus()
					return m, nil
				}
				return m.startJob(selected.job, "")
			}
			var cmd tea.Cmd
			m.list, cmd = m.list.Update(msg)
			return m, cmd
		case modeInput:
			if msg.String() == "enter" {
				command := strings.TrimSpace(m.input.Value())
				if command == "" {
					return m, nil
				}
				m.input.Blur()
				return m.startJob("ucode.command", command)
			}
			var cmd tea.Cmd
			m.input, cmd = m.input.Update(msg)
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
		body = m.list.View()
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
	case modeRunner:
		body = m.viewport.View()
	}
	footer := "Enter select  Esc back  ? help  Ctrl+L redraw  Ctrl+C quit"
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
