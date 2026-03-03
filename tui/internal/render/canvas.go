package render

import (
	"strings"

	"github.com/charmbracelet/lipgloss"
	"udos/tui/internal/protocol"
)

func CropPad(line string, width int) string {
	runes := []rune(line)
	if len(runes) > width {
		return string(runes[:width])
	}
	if len(runes) < width {
		return line + strings.Repeat(" ", width-len(runes))
	}
	return line
}

func RenderHeader(theme Theme, title, subtitle string) string {
	body := CropPad(title, theme.CanvasWidth-4)
	if subtitle != "" {
		body += "\n" + CropPad(subtitle, theme.CanvasWidth-4)
	}
	return theme.Header.Width(theme.CanvasWidth).Render(body)
}

func RenderEvent(theme Theme, event protocol.Event) string {
	lines := event.Lines
	if event.Kind == "teletext" {
		lines = event.Rows
	}
	body := strings.Join(lines, "\n")
	style := theme.Block
	switch event.Style {
	case "accent":
		style = theme.AccentBlock
	case "warn":
		style = theme.WarnBlock
	case "ok":
		style = theme.OKBlock
	}
	title := event.Title
	if title != "" {
		body = lipgloss.NewStyle().Bold(true).Render(title) + "\n" + body
	}
	return style.Width(theme.CanvasWidth).Render(body)
}
