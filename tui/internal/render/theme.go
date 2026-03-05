package render

import "github.com/charmbracelet/lipgloss"

type Theme struct {
	CanvasWidth int
	TeletextUnicode bool
	Header      lipgloss.Style
	Block       lipgloss.Style
	AccentBlock lipgloss.Style
	WarnBlock   lipgloss.Style
	OKBlock     lipgloss.Style
	Muted       lipgloss.Style
	Accent      lipgloss.Style
	Footer      lipgloss.Style
	Error       lipgloss.Style
}

func NewTheme() Theme {
	border := lipgloss.NormalBorder()
	return Theme{
		CanvasWidth: 78,
		TeletextUnicode: false,
		Header: lipgloss.NewStyle().
			Border(border, true).
			BorderForeground(lipgloss.Color("7")).
			Bold(true).
			Padding(0, 1),
		Block: lipgloss.NewStyle().
			Border(border, true).
			BorderForeground(lipgloss.Color("7")).
			Padding(0, 1),
		AccentBlock: lipgloss.NewStyle().
			Border(border, true).
			BorderForeground(lipgloss.Color("6")).
			Padding(0, 1),
		WarnBlock: lipgloss.NewStyle().
			Border(border, true).
			BorderForeground(lipgloss.Color("3")).
			Padding(0, 1),
		OKBlock: lipgloss.NewStyle().
			Border(border, true).
			BorderForeground(lipgloss.Color("2")).
			Padding(0, 1),
		Muted:  lipgloss.NewStyle().Foreground(lipgloss.Color("8")),
		Accent: lipgloss.NewStyle().Foreground(lipgloss.Color("6")).Bold(true),
		Footer: lipgloss.NewStyle().Foreground(lipgloss.Color("8")),
		Error:  lipgloss.NewStyle().Foreground(lipgloss.Color("1")).Bold(true),
	}
}
