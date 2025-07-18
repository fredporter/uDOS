#!/bin/bash
# variable-manager.sh - Variable management system for uDOS

UHOME="${UHOME:-$HOME/uDOS}"
VARIABLES_DIR="$UHOME/uTemplate/variables"

# Set a variable
set_variable() {
  local name="$1"
  local value="$2"
  local scope="${3:-user}"
  
  case "$scope" in
    user)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/user-vars.json" > "/tmp/user-vars.tmp" && mv "/tmp/user-vars.tmp" "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/session.json" > "/tmp/session.tmp" && mv "/tmp/session.tmp" "$VARIABLES_DIR/session.json"
      ;;
    env)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/env.json" > "/tmp/env.tmp" && mv "/tmp/env.tmp" "$VARIABLES_DIR/env.json"
      ;;
  esac
}

# Get a variable
get_variable() {
  local name="$1"
  local scope="${2:-user}"
  
  case "$scope" in
    user)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/session.json"
      ;;
    env)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/env.json"
      ;;
  esac
}

# List all variables
list_variables() {
  local scope="${1:-all}"
  
  case "$scope" in
    user)
      echo "📋 User Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      echo "📋 Session Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/session.json"
      ;;
    env)
      echo "📋 Environment Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/env.json"
      ;;
    all)
      list_variables user
      echo ""
      list_variables session
      echo ""
      list_variables env
      ;;
  esac
}

# Command line interface
case "$1" in
  set)
    set_variable "$2" "$3" "$4"
    echo "✅ Variable set: $2 = $3"
    ;;
  get)
    value=$(get_variable "$2" "$3")
    if [[ -n "$value" ]]; then
      echo "$value"
    else
      echo "❌ Variable not found: $2"
    fi
    ;;
  list)
    list_variables "$2"
    ;;
  *)
    echo "Usage: $0 {set|get|list} [args...]"
    echo "  set <name> <value> [scope]  - Set a variable"
    echo "  get <name> [scope]          - Get a variable"
    echo "  list [scope]                - List variables"
    echo ""
    echo "Scopes: user, session, env, all"
    ;;
esac
