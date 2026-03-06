package render

import (
	"fmt"
	"sort"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/mattn/go-runewidth"
	"udos/tui/internal/protocol"
)

func CropPad(line string, width int) string {
	if width <= 0 {
		return ""
	}
	clean := strings.ReplaceAll(strings.ReplaceAll(line, "\r", " "), "\n", " ")
	if runewidth.StringWidth(clean) > width {
		clean = runewidth.Truncate(clean, width, "")
	}
	if runewidth.StringWidth(clean) < width {
		return clean + strings.Repeat(" ", width-runewidth.StringWidth(clean))
	}
	return clean
}

func RenderHeader(theme Theme, title, subtitle string) string {
	body := CropPad(title, theme.CanvasWidth-4)
	if subtitle != "" {
		body += "\n" + CropPad(subtitle, theme.CanvasWidth-4)
	}
	return theme.Header.Width(theme.CanvasWidth).Render(body)
}

func RenderEvent(theme Theme, event protocol.Event) string {
	switch event.Kind {
	case "rule":
		return theme.Muted.Width(theme.CanvasWidth).Render(strings.Repeat("-", theme.CanvasWidth))
	case "log":
		return renderLog(theme, event)
	case "columns":
		return renderColumns(theme, event)
	}

	lines := event.Lines
	switch event.Kind {
	case "teletext":
		lines = event.Rows
		lines = normalizeTeletextRows(lines, event.Mode, theme.TeletextUnicode)
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

func normalizeTeletextRows(lines []string, mode string, allowUnicode bool) []string {
	if allowUnicode || strings.EqualFold(mode, "blocks") {
		return lines
	}
	mapped := make([]string, 0, len(lines))
	replacer := strings.NewReplacer(
		"░", ".",
		"▒", ":",
		"▓", "*",
		"█", "#",
		"▀", "#",
		"▄", "#",
	)
	for _, line := range lines {
		mapped = append(mapped, replacer.Replace(line))
	}
	return mapped
}

func renderLog(theme Theme, event protocol.Event) string {
	level := strings.ToUpper(strings.TrimSpace(event.Level))
	if level == "" {
		level = "INFO"
	}
	msg := strings.TrimSpace(event.Message)
	if msg == "" && len(event.Lines) > 0 {
		msg = strings.Join(event.Lines, " ")
	}
	if msg == "" {
		msg = "(empty log message)"
	}

	lines := []string{fmt.Sprintf("[%s] %s", level, msg)}
	if len(event.Fields) > 0 {
		keys := make([]string, 0, len(event.Fields))
		for k := range event.Fields {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		for _, key := range keys {
			lines = append(lines, fmt.Sprintf("%s=%s", key, event.Fields[key]))
		}
	}
	eventCopy := event
	eventCopy.Kind = "block"
	eventCopy.Title = "LOG"
	eventCopy.Lines = lines
	if eventCopy.Style == "" {
		if level == "WARN" || level == "WARNING" {
			eventCopy.Style = "warn"
		} else if level == "ERROR" {
			eventCopy.Style = "warn"
		} else {
			eventCopy.Style = "default"
		}
	}
	return RenderEvent(theme, eventCopy)
}

func renderColumns(theme Theme, event protocol.Event) string {
	if len(event.Cols) == 0 {
		return RenderEvent(theme, protocol.Event{
			Kind:  "block",
			Title: event.Title,
			Style: event.Style,
			Lines: []string{"(no columns)"},
		})
	}
	maxCols := len(event.Cols)
	if maxCols > 4 {
		maxCols = 4
	}
	frame := theme.Block.GetHorizontalFrameSize()
	canvasInner := theme.CanvasWidth - frame
	gap := 1
	colWidth := (canvasInner - (maxCols-1)*gap) / maxCols
	if colWidth < 18 {
		// Minimal fallback on narrow terminals: stacked blocks.
		parts := make([]string, 0, maxCols)
		for i := 0; i < maxCols; i++ {
			col := event.Cols[i]
			parts = append(parts, RenderEvent(theme, protocol.Event{
				Kind:  "block",
				Title: col.Title,
				Style: col.Style,
				Lines: col.Lines,
			}))
		}
		return strings.Join(parts, "\n\n")
	}

	renderedCols := make([][]string, 0, maxCols)
	maxLines := 0
	for i := 0; i < maxCols; i++ {
		col := event.Cols[i]
		colLines := make([]string, 0, len(col.Lines)+1)
		if col.Title != "" {
			colLines = append(colLines, CropPad(strings.ToUpper(col.Title), colWidth))
		}
		for _, ln := range col.Lines {
			colLines = append(colLines, CropPad(ln, colWidth))
		}
		if len(colLines) == 0 {
			colLines = append(colLines, CropPad("", colWidth))
		}
		if len(colLines) > maxLines {
			maxLines = len(colLines)
		}
		renderedCols = append(renderedCols, colLines)
	}

	rows := make([]string, 0, maxLines+2)
	if event.Title != "" {
		rows = append(rows, CropPad(strings.ToUpper(event.Title), theme.CanvasWidth-4))
	}
	for row := 0; row < maxLines; row++ {
		parts := make([]string, 0, maxCols)
		for col := 0; col < maxCols; col++ {
			lines := renderedCols[col]
			if row < len(lines) {
				parts = append(parts, lines[row])
			} else {
				parts = append(parts, CropPad("", colWidth))
			}
		}
		rows = append(rows, strings.Join(parts, strings.Repeat(" ", gap)))
	}
	return theme.Block.Width(theme.CanvasWidth).Render(strings.Join(rows, "\n"))
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
