package protocol

type Message struct {
	V      int         `json:"v"`
	Type   string      `json:"type"`
	ID     string      `json:"id"`
	TS     string      `json:"ts,omitempty"`
	Job    string      `json:"job,omitempty"`
	Args   interface{} `json:"args,omitempty"`
	Value  interface{} `json:"value,omitempty"`
	Stream string      `json:"stream,omitempty"`
	Event  *Event      `json:"event,omitempty"`
	Client *ClientInfo `json:"client,omitempty"`
	Caps   *ClientCaps `json:"caps,omitempty"`
	OK     bool        `json:"ok,omitempty"`
	ExitCode int       `json:"exit_code,omitempty"`
	Error  string      `json:"error,omitempty"`
}

type Event struct {
	Kind    string   `json:"kind"`
	Title   string   `json:"title,omitempty"`
	Style   string   `json:"style,omitempty"`
	Lines   []string `json:"lines,omitempty"`
	Message string   `json:"message,omitempty"`
	Level   string   `json:"level,omitempty"`
	Fields  map[string]string `json:"fields,omitempty"`
	Mode    string   `json:"mode,omitempty"`
	Rows    []string `json:"rows,omitempty"`
	Cols    []Column `json:"cols,omitempty"`
	PID     string   `json:"pid,omitempty"`
	Label   string   `json:"label,omitempty"`
	Current int      `json:"current,omitempty"`
	Total   int      `json:"total,omitempty"`
	Status  string   `json:"status,omitempty"`
}

type Column struct {
	Title string   `json:"title,omitempty"`
	Style string   `json:"style,omitempty"`
	Lines []string `json:"lines,omitempty"`
}

type RunArgs struct {
	Command string `json:"command"`
}

type HomeAction struct {
	Key   string `json:"key"`
	Label string `json:"label"`
	Job   string `json:"job"`
}

type ClientInfo struct {
	Name    string `json:"name,omitempty"`
	Version string `json:"version,omitempty"`
}

type ClientCaps struct {
	TTY   bool   `json:"tty,omitempty"`
	Width int    `json:"width,omitempty"`
	Color string `json:"color,omitempty"`
	Paste string `json:"paste,omitempty"`
}
