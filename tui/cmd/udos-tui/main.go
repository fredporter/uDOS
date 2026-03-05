package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"

	"udos/tui/internal/app"
)

func main() {
	model, err := app.NewModel()
	if err != nil {
		fmt.Fprintf(os.Stderr, "udos-tui init failed: %v\n", err)
		os.Exit(1)
	}
	program := tea.NewProgram(
		model,
		tea.WithAltScreen(),
	)
	if _, err := program.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "udos-tui run failed: %v\n", err)
		os.Exit(1)
	}
}
