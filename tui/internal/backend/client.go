package backend

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"udos/tui/internal/protocol"
)

type Client struct {
	cmd    *exec.Cmd
	stdin  io.WriteCloser
	msgs   chan protocol.Message
	errors chan error
}

func Start(repoRoot string) (*Client, error) {
	python := os.Getenv("UDOS_TUI_PYTHON")
	if python == "" {
		python = filepath.Join(repoRoot, ".venv", "bin", "python")
	}
	cmd := exec.Command(python, "-m", "core.tui.protocol_bridge")
	cmd.Dir = repoRoot

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return nil, err
	}
	client := &Client{
		cmd:    cmd,
		stdin:  stdin,
		msgs:   make(chan protocol.Message, 128),
		errors: make(chan error, 8),
	}
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	go client.scan(stdout)
	go client.scanStderr(stderr)
	return client, nil
}

func (c *Client) scan(r io.Reader) {
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		var msg protocol.Message
		if err := json.Unmarshal(scanner.Bytes(), &msg); err != nil {
			c.errors <- err
			continue
		}
		c.msgs <- msg
	}
	if err := scanner.Err(); err != nil {
		c.errors <- err
	}
}

func (c *Client) scanStderr(r io.Reader) {
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		c.errors <- fmt.Errorf(scanner.Text())
	}
}

func (c *Client) Send(msg protocol.Message) error {
	return json.NewEncoder(c.stdin).Encode(msg)
}

func (c *Client) Messages() <-chan protocol.Message {
	return c.msgs
}

func (c *Client) Errors() <-chan error {
	return c.errors
}

func RequestID(prefix string) string {
	return fmt.Sprintf("%s-%d", prefix, time.Now().UnixNano())
}
