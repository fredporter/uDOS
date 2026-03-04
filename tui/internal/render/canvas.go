package render

import (
	"fmt"
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
	switch event.Kind {
	case "teletext":
		lines = event.Rows
	case "progress":
		lines = renderProgressLines(event, theme.CanvasWidth-4)
	}
	lines = cropPadLines(lines, theme.CanvasWidth-4)
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

func cropPadLines(lines []string, width int) []string {
	if len(lines) == 0 {
		return []string{CropPad("", width)}
	}
	rendered := make([]string, 0, len(lines))
	for _, line := range lines {
		rendered = append(rendered, CropPad(line, width))
	}
	return rendered
}

func renderProgressLines(event protocol.Event, width int) []string {
	total := event.Total
	if total <= 0 {
		total = 1
	}
	current := event.Current
	if current < 0 {
		current = 0
	}
	if current > total {
		current = total
	}
	label := event.Label
	if label == "" {
		label = "Progress"
	}
	status := event.Status
	if status == "" {
		status = "running"
	}
	barWidth := width - 18
	if barWidth < 10 {
		barWidth = 10
	}
	filled := int(float64(current) / float64(total) * float64(barWidth))
	if filled > barWidth {
		filled = barWidth
	}
	bar := "[" + strings.Repeat("#", filled) + strings.Repeat(".", barWidth-filled) + "]"
	return []string{
		fmt.Sprintf("%s (%d/%d)", label, current, total),
		bar,
		fmt.Sprintf("status: %s", status),
	}
}
