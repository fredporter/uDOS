#!/bin/bash

SETUP_FILE="${1:-$UHOME/uTemplate/getdata-user-setup.md}"
current_var=""
current_prompt=""
current_default=""
current_type=""

selections=()
while IFS= read -r line; do
  case "$line" in
    DATA:*)
      current_var="${line#DATA: }"
      ;;
    ASK:*)
      current_prompt="${line#ASK: }"
      ;;
    DEFAULT:*)
      DEFAULT_LINE="${line#DEFAULT: }"
      if [[ "$DEFAULT_LINE" == \$DATASET:* ]]; then
        dataset_path="${DEFAULT_LINE#\$DATASET:}"
        if [[ -f "$UHOME/uTemplate/$dataset_path" ]]; then
          current_default=$(paste -sd, "$UHOME/uTemplate/$dataset_path")
        else
          echo "⚠️ Dataset file not found: $UHOME/uTemplate/$dataset_path"
          current_default=""
        fi
      else
        current_default="$DEFAULT_LINE"
      fi
      ;;
    TYPE:*)
      current_type="${line#TYPE: }"

      # Prompt only when TYPE is defined (end of a block)
      if [[ -t 0 ]]; then
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
        elif [[ "$current_type" == "freetext" ]]; then
          read -rp "🔹 $current_prompt [$current_default]: " value
          [ -z "$value" ] && value="$current_default"
          # Limit to 120 characters and clean up special characters
          value="${value:0:120}"
          value=$(echo "$value" | sed 's/[^a-zA-Z0-9 .,/_-]//g')
        elif [[ "$current_type" == "shorttext" ]]; then
          read -rp "🔹 $current_prompt [$current_default]: " value
          [ -z "$value" ] && value="$current_default"
          # Limit to 10 characters and allow only A-Z, a-z, 0-9, space, dash
          value="${value:0:10}"
          value=$(echo "$value" | sed 's/[^a-zA-Z0-9 -]//g')
        elif [[ "$current_type" == "yesno" ]]; then
          while true; do
            read -rp "🔹 $current_prompt [Y/n] (default: $current_default): " value
            value="${value,,}"  # lowercase
            [[ -z "$value" ]] && value="$current_default"
            case "$value" in
              y|yes) value="yes"; break ;;
              n|no) value="no"; break ;;
              *) echo "Please enter yes or no." ;;
            esac
          done
        elif [[ "$current_type" == "multiple" ]]; then
          echo "📋 $current_prompt"
          IFS=',' read -ra options <<< "$current_default"
          select opt in "${options[@]}" "Done"; do
            [[ "$opt" == "Done" ]] && break
            selections+=("$opt")
          done
          value=$(IFS=','; echo "${selections[*]}")
        else
          read -rp "🔹 $current_prompt [$current_default]: " value
        fi
        [ -z "$value" ] && value="$current_default"
      else
        value="$current_default"
      fi

      current_var=$(echo "$current_var" | xargs)
      value=$(echo "$value" | xargs)
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