#!/bin/bash

SETUP_FILE="${1:-$UHOME/uTemplate/getdata-user-setup.md}"
current_var=""
current_prompt=""
current_default=""
current_type=""

while IFS= read -r line; do
  case "$line" in
    DATA:*)
      current_var="${line#DATA: }"
      ;;
    ASK:*)
      current_prompt="${line#ASK: }"
      ;;
    DEFAULT:*)
      current_default="${line#DEFAULT: }"
      ;;
    TYPE:*)
      current_type="${line#TYPE: }"

      # Prompt only when TYPE is defined (end of a block)
      if [ ! -t 0 ]; then
        value="$current_default"
      else
        echo ""
        if [[ "$current_type" == "password" ]]; then
          read -rsp "🔒 $current_prompt [$current_default]: " value
          echo ""
        elif [[ "$current_type" == "select" ]]; then
          echo "📋 $current_prompt"
          IFS=',' read -ra options <<< "$current_default"
          select opt in "${options[@]}"; do
            value="$opt"
            break
          done
        else
          read -rp "🔹 $current_prompt [$current_default]: " value
        fi

        [ -z "$value" ] && value="$current_default"
      fi

      export "$current_var"="$value"
      echo "export $current_var=\"$value\"" >> "$UHOME/sandbox/user-vars.env"

      # Reset current vars
      current_var=""
      current_prompt=""
      current_default=""
      current_type=""
      ;;
  esac
done < "$SETUP_FILE"