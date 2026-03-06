package primitives

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
)

type MenuItem struct {
	Key   string
	Label string
	Desc  string
	Value string
}

func (i MenuItem) TitleText() string {
	if i.Key == "" {
		return i.Label
	}
	return fmt.Sprintf("%s. %s", i.Key, i.Label)
}

func (i MenuItem) Title() string       { return i.TitleText() }
func (i MenuItem) Description() string { return i.Desc }
func (i MenuItem) FilterValue() string { return i.Label + " " + i.Desc + " " + i.Value }

type SelectOne struct {
	Title string
	List  list.Model
}

func NewSelectOne(title string, items []MenuItem, width, height int, filter bool) SelectOne {
	listItems := make([]list.Item, 0, len(items))
	for _, item := range items {
		listItems = append(listItems, item)
	}
	l := list.New(listItems, list.NewDefaultDelegate(), width, height)
	l.Title = title
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(filter)
	return SelectOne{Title: title, List: l}
}

func (s SelectOne) Update(msg tea.Msg) (SelectOne, tea.Cmd) {
	var cmd tea.Cmd
	s.List, cmd = s.List.Update(msg)
	return s, cmd
}

func (s SelectOne) Selected() (MenuItem, bool) {
	item, ok := s.List.SelectedItem().(MenuItem)
	return item, ok
}

func (s SelectOne) View() string {
	return s.List.View()
}

type SelectMany struct {
	SelectOne
	selected map[string]bool
}

func NewSelectMany(title string, items []MenuItem, width, height int, filter bool) SelectMany {
	return SelectMany{
		SelectOne: NewSelectOne(title, items, width, height, filter),
		selected:  map[string]bool{},
	}
}

func (s SelectMany) Update(msg tea.Msg) (SelectMany, tea.Cmd) {
	if key, ok := msg.(tea.KeyMsg); ok {
		switch key.String() {
		case " ":
			if item, ok := s.Selected(); ok {
				value := item.Value
				if value == "" {
					value = item.Label
				}
				s.selected[value] = !s.selected[value]
				return s, nil
			}
		case "a":
			for _, entry := range s.List.Items() {
				if item, ok := entry.(MenuItem); ok {
					value := item.Value
					if value == "" {
						value = item.Label
					}
					s.selected[value] = true
				}
			}
			return s, nil
		case "x":
			s.selected = map[string]bool{}
			return s, nil
		}
	}
	var cmd tea.Cmd
	s.SelectOne, cmd = s.SelectOne.Update(msg)
	return s, cmd
}

func (s SelectMany) Values() []string {
	values := make([]string, 0, len(s.selected))
	for value, on := range s.selected {
		if on {
			values = append(values, value)
		}
	}
	return values
}

type Input struct {
	Title      string
	Model      textinput.Model
	ValidateFn func(string) error
	Error      string
}

func NewInput(title, placeholder string, width int, validateFn func(string) error) Input {
	model := textinput.New()
	model.Placeholder = placeholder
	model.CharLimit = 512
	model.Width = width
	return Input{Title: title, Model: model, ValidateFn: validateFn}
}

func (i Input) Update(msg tea.Msg) (Input, tea.Cmd) {
	var cmd tea.Cmd
	i.Model, cmd = i.Model.Update(msg)
	i.Error = ""
	return i, cmd
}

func (i *Input) Focus() { i.Model.Focus() }

func (i *Input) Blur() { i.Model.Blur() }

func (i Input) Value() string { return i.Model.Value() }

func (i *Input) Validate() bool {
	if i.ValidateFn == nil {
		i.Error = ""
		return true
	}
	err := i.ValidateFn(strings.TrimSpace(i.Model.Value()))
	if err != nil {
		i.Error = err.Error()
		return false
	}
	i.Error = ""
	return true
}

func (i Input) View() string {
	body := i.Model.View()
	if i.Error != "" {
		return body + "\n" + "error: " + i.Error
	}
	return body
}

type Textarea struct {
	Title      string
	Model      textarea.Model
	ValidateFn func(string) error
	Error      string
	PasteSafe  bool
}

func NewTextarea(title string, width, height int, validateFn func(string) error, pasteSafe bool) Textarea {
	model := textarea.New()
	model.SetWidth(width)
	model.SetHeight(height)
	model.ShowLineNumbers = false
	return Textarea{
		Title:      title,
		Model:      model,
		ValidateFn: validateFn,
		PasteSafe:  pasteSafe,
	}
}

type Confirm struct {
	Title      string
	DefaultYes bool
}

type PickerPath struct {
	Title     string
	StartDir  string
	MustExist bool
}

type PickerCommand struct {
	Title  string
	Select SelectOne
}

func NewPickerCommand(title string, commands []string, width, height int) PickerCommand {
	items := make([]MenuItem, 0, len(commands))
	for idx, command := range commands {
		items = append(items, MenuItem{
			Key:   fmt.Sprintf("%d", idx+1),
			Label: command,
			Desc:  "Command",
			Value: command,
		})
	}
	return PickerCommand{
		Title:  title,
		Select: NewSelectOne(title, items, width, height, true),
	}
}
