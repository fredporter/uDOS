#!/usr/bin/env python3
import sys, re, json, os

def load_vars():
    try:
        with open(os.path.join(os.path.dirname(__file__), "vars/user-vars.json")) as f:
            return json.load(f)
    except Exception:
        return {}

def save_vars(vars_dict):
    with open(os.path.join(os.path.dirname(__file__), "vars/user-vars.json"), "w") as f:
        json.dump(vars_dict, f, indent=2)

def substitute_vars(line, vars_dict):
    def repl(match):
        key = match.group(1)
        return str(vars_dict.get(key, "{"+key+"}"))
    return re.sub(r"\{(\w+)\}", repl, line)

def run_ucode(lines):
    vars_dict = load_vars()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("'") or line.startswith("#"):
            continue
        # SET command
        m = re.match(r"SET (\w+) = \"?([^\"]+)\"?", line)
        if m:
            vars_dict[m.group(1)] = m.group(2)
            continue
        # PRINT command
        m = re.match(r"PRINT (.+)", line)
        if m:
            out = substitute_vars(m.group(1), vars_dict)
            print(out)
            continue
        # LOG command
        m = re.match(r"LOG (.+)", line)
        if m:
            out = substitute_vars(m.group(1), vars_dict)
            with open("logs/ucode.log", "a") as logf:
                logf.write(out + "\n")
            continue
        # TODO: Add IF/ELSE, FOR/NEXT, DATASET, etc.
        print(f"[uCode] (unhandled): {line}")
    save_vars(vars_dict)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ucode-interpreter.py <script.md>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        lines = [l for l in f if not l.strip().startswith("LANGUAGE:")]
    run_ucode(lines)