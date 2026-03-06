package app

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"

	"udos/tui/internal/backend"
	"udos/tui/internal/primitives"
	"udos/tui/internal/protocol"
	"udos/tui/internal/render"
)

type screenMode string

const (
	modeHome         screenMode = "home"
	modeInput        screenMode = "input"
	modeAsk          screenMode = "ask"
	modePath         screenMode = "path"
	modeRunner       screenMode = "runner"
	minTerminalWidth            = 25
	minInputWidth               = 8
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
	staticItems  []primitives.MenuItem
	selectOne    primitives.SelectOne
	input        primitives.Input
	askInput     primitives.Input
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

type startupMenuConfig struct {
	Items []startupMenuItem `json:"items"`
}

type startupMenuItem struct {
	Key     string `json:"key"`
	Label   string `json:"label"`
	Desc    string `json:"desc"`
	Job     string `json:"job"`
	Command string `json:"command"`
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
	items := startupMenuItems(repoRoot)
	selectOne := primitives.NewSelectOne("uDOS v1.5", items, 78, 12, true)
	input := primitives.NewInput("CUSTOM COMMAND", "Enter ucode command", 72, nil)
	askInput := primitives.NewInput("FREEFORM QUESTION", "Ask a question (runs: OK ASK <prompt>)", 72, nil)
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
		theme:       render.NewTheme(),
		mode:        modeHome,
		staticItems: items,
		selectOne:   selectOne,
		input:       input,
		askInput:    askInput,
		pathPicker:  pathPicker,
		pathInput:   pathInput,
		viewport:    vp,
		help:        help.New(),
		spinner:     spin,
		backend:     client,
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
	seq := []screenMode{modeHome, modeInput, modeAsk, modePath, modeRunner}
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
		m.askInput.Blur()
		m.pathInput.Blur()
	} else if next == modeAsk {
		m.askInput.Focus()
		m.input.Blur()
		m.pathInput.Blur()
	} else if next == modePath {
		m.pathInput.Focus()
		m.input.Blur()
		m.askInput.Blur()
	} else {
		m.input.Blur()
		m.askInput.Blur()
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
		m.theme.CanvasWidth = m.computeCanvasWidth(msg.Width)
			m.selectOne.List.SetWidth(max(minTerminalWidth, m.theme.CanvasWidth-2))
			inputWidth := max(minInputWidth, m.theme.CanvasWidth-6)
			m.input.Model.Width = inputWidth
			m.askInput.Model.Width = inputWidth
			m.pathInput.Model.Width = inputWidth
		m.viewport.Width = max(minTerminalWidth, m.theme.CanvasWidth)
		m.viewport.Height = max(8, msg.Height-8)
		m.refreshViewportContent()
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
						m.selectOne.List.SetItems(actionsToListItems(actions, m.staticItems))
					}
				}
				if jobID, ok := value["job_id"].(string); ok {
					m.currentJobID = jobID
				}
			}
		}
		if msg.msg.Type == "event" && msg.msg.Event != nil {
			m.events = append(m.events, *msg.msg.Event)
			m.refreshViewportContent()
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
			case "f1":
				m.showHelp = !m.showHelp
				return m, nil
			case "?":
				if m.mode != modeAsk {
					m.mode = modeAsk
					m.askInput.Focus()
					m.statusLine = "freeform prompt mode"
					return m, nil
				}
			case "m":
				m.theme.TeletextUnicode = !m.theme.TeletextUnicode
			if m.theme.TeletextUnicode {
				m.statusLine = "teletext mode: unicode blocks"
			} else {
				m.statusLine = "teletext mode: ascii"
			}
			m.refreshViewportContent()
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
			fallthrough
		case "escape":
				if m.mode == modeRunner || m.mode == modeInput || m.mode == modeAsk || m.mode == modePath {
					m.mode = modeHome
					return m, nil
				}
		}

		switch m.mode {
		case modeHome:
			switch msg.String() {
			case "n":
				m.moveHomeSelection(1, 0)
				return m, nil
			case "N":
				m.moveHomeSelection(-1, 0)
				return m, nil
			case "up":
				m.moveHomeSelection(-1, 0)
				return m, nil
			case "down":
				m.moveHomeSelection(1, 0)
				return m, nil
			case "left":
				m.moveHomeSelection(0, -1)
				return m, nil
			case "right":
				m.moveHomeSelection(0, 1)
				return m, nil
			}
			if selected, ok := m.shortcutSelection(msg.String()); ok {
				return m.runSelection(selected)
			}
			if msg.String() == "enter" {
				selected, ok := m.selectOne.Selected()
				if !ok {
					return m, nil
				}
				return m.runSelection(selected)
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
			case modeAsk:
				if msg.String() == "enter" {
					question := sanitizeSingleLineInput(m.askInput.Value())
					if question == "" {
						return m, nil
					}
					m.askInput.Blur()
					return m.startJob("ucode.command", "OK ASK "+question)
				}
				var cmd tea.Cmd
				m.askInput, cmd = m.askInput.Update(msg)
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
			if msg.String() == "enter" || msg.String() == "h" {
				m.mode = modeHome
				return m, nil
			}
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
		"Bubble Tea + Lip Gloss | v1.5 JSONL runtime",
	)
	body := ""
	switch m.mode {
	case modeHome:
		body = m.renderHomeMenu()
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
	case modeAsk:
		body = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "FREEFORM PROMPT",
				Style: "accent",
				Lines: []string{
					"Type your question and press Enter",
					m.askInput.View(),
				},
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
	footer := m.footerHint()
	if m.statusLine != "" {
		footer = footer + " | " + m.statusLine
	}
	if m.lastError != "" {
		footer = footer + " | error: " + m.lastError
	}
	return strings.Join([]string{
		header,
		body,
		m.theme.Footer.Width(m.theme.CanvasWidth).Render(render.CropPad(footer, m.theme.CanvasWidth)),
	}, "\n\n")
}

func (m Model) runSelection(selected primitives.MenuItem) (tea.Model, tea.Cmd) {
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
	if command, ok := strings.CutPrefix(selected.Value, "ucode.command:"); ok {
		command = sanitizeSingleLineInput(command)
		if command == "" {
			return m, nil
		}
		return m.startJob("ucode.command", command)
	}
	return m.startJob(selected.Value, "")
}

func (m Model) shortcutSelection(key string) (primitives.MenuItem, bool) {
	for _, entry := range m.selectOne.List.Items() {
		item, ok := entry.(primitives.MenuItem)
		if !ok {
			continue
		}
		if item.Key == key {
			return item, true
		}
	}
	return primitives.MenuItem{}, false
}

func (m Model) footerHint() string {
	switch m.mode {
	case modeHome:
		return "Key/Enter run item  n next  N prev  ? freeform prompt  F1 help  m teletext  Tab next  Shift+Tab prev  Ctrl+R refresh  Ctrl+L redraw  Ctrl+C quit"
	case modeInput:
		return "Type command  Enter run  Esc back  ? freeform prompt  F1 help  Tab next  Shift+Tab prev  m teletext  Ctrl+R refresh  Ctrl+L redraw  Ctrl+C quit"
	case modeAsk:
		return "Type freeform question  Enter run OK ASK  Esc back  F1 help  Tab next  Shift+Tab prev  m teletext  Ctrl+R refresh  Ctrl+L redraw  Ctrl+C quit"
	case modePath:
		return "Type path  Enter run READ <path>  Esc back  ? freeform prompt  F1 help  Tab next  Shift+Tab prev  m teletext  Ctrl+R refresh  Ctrl+L redraw  Ctrl+C quit"
	case modeRunner:
		return "Enter/H home  Esc back  PgUp/PgDn scroll  ? freeform prompt  F1 help  Tab next  Shift+Tab prev  m teletext  Ctrl+R rerun/refresh  Ctrl+L redraw  Ctrl+C quit"
	default:
		return "? freeform prompt  F1 help  Tab next  Shift+Tab prev  Ctrl+R refresh  Ctrl+L redraw  Ctrl+C quit"
	}
}

func (m Model) renderHomeMenu() string {
	menuItems := make([]primitives.MenuItem, 0, len(m.selectOne.List.Items()))
	for _, entry := range m.selectOne.List.Items() {
		if item, ok := entry.(primitives.MenuItem); ok {
			menuItems = append(menuItems, item)
		}
	}
	if len(menuItems) == 0 {
		menu := render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "STARTUP MENU",
				Style: "accent",
				Lines: []string{"(no menu items)"},
			},
		)
		preview := render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "PREDICTIVE COMMAND",
				Style: "ok",
				Lines: []string{"No selection"},
			},
		)
		return strings.Join([]string{menu, preview}, "\n\n")
	}

	selected := m.selectOne.List.Index()
	if selected < 0 {
		selected = 0
	}
	colCount := menuColumnCount(m.theme.CanvasWidth)
	if colCount == 1 {
		lines := make([]string, 0, len(menuItems))
		for idx, item := range menuItems {
			marker := " "
			if idx == selected {
				marker = ">"
			}
			key := strings.TrimSpace(item.Key)
			if key == "" {
				key = " "
			}
			lines = append(lines, fmt.Sprintf("%s [%s] %s", marker, key, item.Label))
		}
		menu := render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "STARTUP MENU",
				Style: "accent",
				Lines: lines,
			},
		)
		preview := m.renderPredictiveCommandBlock(menuItems, selected)
		return strings.Join([]string{menu, preview}, "\n\n")
	}

	rowCount := (len(menuItems) + colCount - 1) / colCount
	columns := make([]protocol.Column, 0, colCount)
	for col := 0; col < colCount; col++ {
		lines := make([]string, 0, rowCount)
		for row := 0; row < rowCount; row++ {
			idx := row*colCount + col
			if idx >= len(menuItems) {
				continue
			}
			item := menuItems[idx]
			marker := " "
			if idx == selected {
				marker = ">"
			}
			key := strings.TrimSpace(item.Key)
			if key == "" {
				key = " "
			}
			lines = append(lines, fmt.Sprintf("%s [%s] %s", marker, key, item.Label))
		}
		if len(lines) == 0 {
			lines = append(lines, "")
		}
		columns = append(columns, protocol.Column{
			Title: fmt.Sprintf("MENU %d", col+1),
			Lines: lines,
		})
	}

	menu := render.RenderEvent(
		m.theme,
		protocol.Event{
			Kind:  "columns",
			Title: "STARTUP MENU",
			Cols:  columns,
		},
	)
	preview := m.renderPredictiveCommandBlock(menuItems, selected)
	return strings.Join([]string{menu, preview}, "\n\n")
}

func (m Model) renderPredictiveCommandBlock(menuItems []primitives.MenuItem, selected int) string {
	if len(menuItems) == 0 {
		return render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "PREDICTIVE COMMAND",
				Style: "ok",
				Lines: []string{"No selection"},
			},
		)
	}
	selected = max(0, min(selected, len(menuItems)-1))
	item := menuItems[selected]
	job, command := predictSelection(item)
	maxLen := max(16, m.theme.CanvasWidth-12)
	lines := []string{
		"selection: " + compactLine(item.Label, maxLen),
		"job: " + compactLine(job, maxLen),
	}
	if command != "" {
		lines = append(lines, "command: "+compactLine(command, maxLen))
	}
	lines = append(lines, "Enter executes this route")
	return render.RenderEvent(
		m.theme,
		protocol.Event{
			Kind:  "block",
			Title: "PREDICTIVE COMMAND",
			Style: "ok",
			Lines: lines,
		},
	)
}

func predictSelection(selected primitives.MenuItem) (job string, command string) {
	if selected.Value == "picker.path" {
		return "ucode.command", "READ <path>"
	}
	if selected.Value == "custom.command" {
		return "ucode.command", "<typed command>"
	}
	if cmd, ok := strings.CutPrefix(selected.Value, "ucode.command:"); ok {
		return "ucode.command", sanitizeSingleLineInput(cmd)
	}
	return selected.Value, ""
}

func menuColumnCount(canvasWidth int) int {
	if canvasWidth >= 110 {
		return 3
	}
	if canvasWidth < 70 {
		return 1
	}
	return 2
}

func startupMenuItems(repoRoot string) []primitives.MenuItem {
	items := append([]primitives.MenuItem{}, actionItems()...)
	items = append(items, defaultScriptItems()...)
	items = append(items, discoveredScriptItems(repoRoot)...)
	items = append(items, customStartupMenuItems(repoRoot)...)
	return dedupeMenuItems(items)
}

func defaultScriptItems() []primitives.MenuItem {
	return []primitives.MenuItem{
		{
			Key:   "s",
			Label: "Startup Script",
			Desc:  "Run memory/bank/system/startup-script.md",
			Value: "ucode.command:RUN memory/bank/system/startup-script.md",
		},
		{
			Key:   "r",
			Label: "Reboot Script",
			Desc:  "Run memory/bank/system/reboot-script.md",
			Value: "ucode.command:RUN memory/bank/system/reboot-script.md",
		},
	}
}

func discoveredScriptItems(repoRoot string) []primitives.MenuItem {
	roots := []string{
		filepath.Join(repoRoot, "memory", "user", "system"),
		filepath.Join(repoRoot, "memory", "bank", "system"),
	}
	var paths []string
	seen := map[string]bool{}
	for _, root := range roots {
		matches, _ := filepath.Glob(filepath.Join(root, "*.md"))
		for _, path := range matches {
			base := filepath.Base(path)
			if !strings.HasSuffix(base, "-script.md") && !strings.HasSuffix(base, ".script.md") {
				continue
			}
			rel := relPath(repoRoot, path)
			if rel == "" || seen[rel] {
				continue
			}
			seen[rel] = true
			paths = append(paths, rel)
		}
	}
	sort.Strings(paths)
	items := make([]primitives.MenuItem, 0, len(paths))
	for idx, rel := range paths {
		label := strings.TrimSuffix(filepath.Base(rel), filepath.Ext(rel))
		items = append(items, primitives.MenuItem{
			Key:   fmt.Sprintf("f%d", idx+1),
			Label: "Script: " + label,
			Desc:  "Run " + rel,
			Value: "ucode.command:RUN " + rel,
		})
	}
	return items
}

func customStartupMenuItems(repoRoot string) []primitives.MenuItem {
	path := filepath.Join(repoRoot, "memory", "bank", "private", "tui-startup-menu.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil
	}
	var config startupMenuConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil
	}
	items := make([]primitives.MenuItem, 0, len(config.Items))
	for _, entry := range config.Items {
		value := strings.TrimSpace(entry.Job)
		if cmd := sanitizeSingleLineInput(entry.Command); cmd != "" {
			value = "ucode.command:" + cmd
		}
		if value == "" || strings.TrimSpace(entry.Label) == "" {
			continue
		}
		items = append(items, primitives.MenuItem{
			Key:   strings.TrimSpace(entry.Key),
			Label: strings.TrimSpace(entry.Label),
			Desc:  strings.TrimSpace(entry.Desc),
			Value: value,
		})
	}
	return items
}

func dedupeMenuItems(items []primitives.MenuItem) []primitives.MenuItem {
	result := make([]primitives.MenuItem, 0, len(items))
	seenValue := map[string]bool{}
	usedKey := map[string]bool{}
	keyPool := []string{
		"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
		"n", "o", "p", "q", "t", "u", "v", "w", "x", "y", "z",
		"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
		"N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
	}
	nextKey := 0
	for _, item := range items {
		if item.Value == "" || seenValue[item.Value] {
			continue
		}
		key := strings.TrimSpace(item.Key)
		if key != "" && usedKey[key] {
			key = ""
		}
		if key == "" {
			for {
				if nextKey >= len(keyPool) {
					break
				}
				candidate := keyPool[nextKey]
				nextKey++
				if !usedKey[candidate] {
					key = candidate
					break
				}
			}
		}
		item.Key = key
		if key != "" {
			usedKey[key] = true
		}
		seenValue[item.Value] = true
		result = append(result, item)
	}
	return result
}

func relPath(root, path string) string {
	rel, err := filepath.Rel(root, path)
	if err != nil {
		return ""
	}
	return filepath.ToSlash(rel)
}

func (m Model) computeCanvasWidth(termWidth int) int {
	frame := m.maxFrameWidth()
	contentWidth := termWidth - frame
	if contentWidth < minTerminalWidth {
		return minTerminalWidth
	}
	return contentWidth
}

func (m Model) maxFrameWidth() int {
	frames := []int{
		m.theme.Header.GetHorizontalFrameSize(),
		m.theme.Block.GetHorizontalFrameSize(),
		m.theme.AccentBlock.GetHorizontalFrameSize(),
		m.theme.WarnBlock.GetHorizontalFrameSize(),
		m.theme.OKBlock.GetHorizontalFrameSize(),
	}
	maxFrame := 0
	for _, frame := range frames {
		if frame > maxFrame {
			maxFrame = frame
		}
	}
	return maxFrame
}

func (m Model) renderEvents() string {
	rendered := make([]string, 0, len(m.events))
	for _, event := range m.events {
		rendered = append(rendered, render.RenderEvent(m.theme, event))
	}
	return strings.Join(rendered, "\n\n")
}

func (m *Model) refreshViewportContent() {
	if m.mode == modeRunner {
		m.viewport.SetContent(m.renderRunnerContent())
		return
	}
	m.viewport.SetContent(m.renderEvents())
}

func (m Model) renderRunnerContent() string {
	if len(m.events) == 0 {
		return render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "RUNNER",
				Style: "accent",
				Lines: []string{"Waiting for runtime events..."},
			},
		)
	}

	colCount := runnerColumnCount(m.theme.CanvasWidth)
	statusLines := m.runnerStatusLines()
	eventLines := m.recentEventLines(10)
	logLines := m.recentLogLines(10)

	var summary string
	if colCount == 1 {
		lines := []string{"STATUS"}
		lines = append(lines, statusLines...)
		lines = append(lines, "")
		lines = append(lines, "RECENT")
		lines = append(lines, eventLines...)
		if len(logLines) > 0 {
			lines = append(lines, "")
			lines = append(lines, "LOG")
			lines = append(lines, logLines...)
		}
		summary = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "block",
				Title: "RUNNER SUMMARY",
				Style: "accent",
				Lines: lines,
			},
		)
	} else if colCount == 2 {
		summary = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "columns",
				Title: "RUNNER SUMMARY",
				Cols: []protocol.Column{
					{Title: "STATUS", Lines: statusLines},
					{Title: "RECENT", Lines: eventLines},
				},
			},
		)
	} else {
		summary = render.RenderEvent(
			m.theme,
			protocol.Event{
				Kind:  "columns",
				Title: "RUNNER SUMMARY",
				Cols: []protocol.Column{
					{Title: "STATUS", Lines: statusLines},
					{Title: "RECENT", Lines: eventLines},
					{Title: "LOG", Lines: logLines},
				},
			},
		)
	}

	tailStart := len(m.events) - 2
	if tailStart < 0 {
		tailStart = 0
	}
	details := make([]string, 0, len(m.events)-tailStart)
	for _, event := range m.events[tailStart:] {
		details = append(details, render.RenderEvent(m.theme, event))
	}

	if len(details) == 0 {
		return summary
	}
	return strings.Join([]string{summary, strings.Join(details, "\n\n")}, "\n\n")
}

func (m Model) runnerStatusLines() []string {
	lines := []string{}
	if m.lastJob != "" {
		lines = append(lines, "job: "+compactLine(m.lastJob, 44))
	}
	if m.currentJobID != "" {
		lines = append(lines, "id: "+compactLine(m.currentJobID, 44))
	}
	if m.statusLine != "" {
		lines = append(lines, "state: "+compactLine(m.statusLine, 44))
	}
	if m.lastError != "" {
		lines = append(lines, "error: "+compactLine(m.lastError, 44))
	}
	if len(lines) == 0 {
		lines = append(lines, "state: running")
	}
	return lines
}

func (m Model) recentEventLines(limit int) []string {
	if limit <= 0 {
		limit = 8
	}
	start := len(m.events) - limit
	if start < 0 {
		start = 0
	}
	lines := make([]string, 0, len(m.events)-start)
	for _, event := range m.events[start:] {
		kind := strings.ToUpper(strings.TrimSpace(event.Kind))
		if kind == "" {
			kind = "EVENT"
		}
		detail := strings.TrimSpace(event.Title)
		if detail == "" {
			detail = strings.TrimSpace(event.Message)
		}
		if detail == "" && len(event.Lines) > 0 {
			detail = strings.TrimSpace(event.Lines[0])
		}
		if detail == "" {
			lines = append(lines, kind)
		} else {
			lines = append(lines, kind+": "+compactLine(detail, 44))
		}
	}
	if len(lines) == 0 {
		return []string{"No events"}
	}
	return lines
}

func (m Model) recentLogLines(limit int) []string {
	if limit <= 0 {
		limit = 8
	}
	lines := make([]string, 0, limit)
	for idx := len(m.events) - 1; idx >= 0 && len(lines) < limit; idx-- {
		event := m.events[idx]
		if !strings.EqualFold(event.Kind, "log") {
			continue
		}
		level := strings.ToUpper(strings.TrimSpace(event.Level))
		if level == "" {
			level = "INFO"
		}
		msg := strings.TrimSpace(event.Message)
		if msg == "" && len(event.Lines) > 0 {
			msg = strings.TrimSpace(event.Lines[0])
		}
		if msg == "" {
			msg = "(empty)"
		}
		lines = append(lines, "["+level+"] "+compactLine(msg, 44))
	}
	for i, j := 0, len(lines)-1; i < j; i, j = i+1, j-1 {
		lines[i], lines[j] = lines[j], lines[i]
	}
	if len(lines) == 0 {
		return []string{"No logs"}
	}
	return lines
}

func runnerColumnCount(canvasWidth int) int {
	if canvasWidth >= 120 {
		return 3
	}
	if canvasWidth < 70 {
		return 1
	}
	return 2
}

func compactLine(value string, maxLen int) string {
	text := strings.TrimSpace(value)
	if maxLen <= 0 || len(text) <= maxLen {
		return text
	}
	if maxLen <= 3 {
		return text[:maxLen]
	}
	return text[:maxLen-3] + "..."
}

func (m *Model) moveHomeSelection(deltaRow, deltaCol int) {
	items := m.selectOne.List.Items()
	if len(items) == 0 {
		return
	}

	colCount := menuColumnCount(m.theme.CanvasWidth)
	if colCount < 1 {
		colCount = 1
	}
	rowCount := (len(items) + colCount - 1) / colCount
	current := m.selectOne.List.Index()
	if current < 0 {
		current = 0
	}
	if current >= len(items) {
		current = len(items) - 1
	}

	row := current / colCount
	col := current % colCount
	row = max(0, min(row+deltaRow, rowCount-1))
	col = max(0, min(col+deltaCol, colCount-1))

	next := row*colCount + col
	for next >= len(items) && col > 0 {
		col--
		next = row*colCount + col
	}
	for next >= len(items) && row > 0 {
		row--
		next = row*colCount + col
	}
	next = max(0, min(next, len(items)-1))
	m.selectOne.List.Select(next)
}

func actionsToListItems(raw []interface{}, fallbackItems []primitives.MenuItem) []list.Item {
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
	for _, fallback := range fallbackItems {
		items = append(items, fallback)
	}
	items = listItemsFromMenu(dedupeMenuItems(menuItemsFromList(items)))
	if len(items) == 0 {
		return listItemsFromMenu(actionItems())
	}
	return items
}

func menuItemsFromList(items []list.Item) []primitives.MenuItem {
	out := make([]primitives.MenuItem, 0, len(items))
	for _, item := range items {
		if menu, ok := item.(primitives.MenuItem); ok {
			out = append(out, menu)
		}
	}
	return out
}

func listItemsFromMenu(items []primitives.MenuItem) []list.Item {
	out := make([]list.Item, 0, len(items))
	for _, item := range items {
		out = append(out, item)
	}
	return out
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
