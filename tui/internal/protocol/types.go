package protocol

type Message struct {
	V     int         `json:"v"`
	Type  string      `json:"type"`
	ID    string      `json:"id"`
	TS    string      `json:"ts,omitempty"`
	Job   string      `json:"job,omitempty"`
	Args  interface{} `json:"args,omitempty"`
	Value interface{} `json:"value,omitempty"`
	Stream string     `json:"stream,omitempty"`
	Event *Event      `json:"event,omitempty"`
	OK    bool        `json:"ok,omitempty"`
	ExitCode int      `json:"exit_code,omitempty"`
	Error string      `json:"error,omitempty"`
}

type Event struct {
	Kind  string   `json:"kind"`
	Title string   `json:"title,omitempty"`
	Style string   `json:"style,omitempty"`
	Lines []string `json:"lines,omitempty"`
	Mode  string   `json:"mode,omitempty"`
	Rows  []string `json:"rows,omitempty"`
}

type RunArgs struct {
	Command string `json:"command"`
}

type HomeAction struct {
	Key   string `json:"key"`
	Label string `json:"label"`
	Job   string `json:"job"`
}
