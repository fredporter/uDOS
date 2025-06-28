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

      echo ""
      if [[ "$current_type" == "password" ]]; then
        while true; do
          read -rsp "🔒 $current_prompt [$current_default] (enter 'd' to use default): " value
          echo ""
          [[ "$value" == "d" || -z "$value" ]] && value="$current_default"
          break
        done
      elif [[ "$current_type" == "select" ]]; then
        echo "📋 $current_prompt"
        IFS=',' read -ra options <<< "$current_default"
        select opt in "${options[@]}"; do
          value="$opt"
          break
        done
      elif [[ "$current_type" == "freetext" ]]; then
        while true; do
          read -rp "🔹 $current_prompt [$current_default] (enter 'd' to use default): " value
          [[ "$value" == "d" || -z "$value" ]] && value="$current_default"
          value="${value:0:120}"
          value=$(echo "$value" | sed 's/[^a-zA-Z0-9 .,/_-]//g')
          break
        done
      elif [[ "$current_type" == "shorttext" ]]; then
        while true; do
          read -rp "🔹 $current_prompt [$current_default] (enter 'd' to use default): " value
          [[ "$value" == "d" || -z "$value" ]] && value="$current_default"
          value="${value:0:10}"
          value=$(echo "$value" | sed 's/[^a-zA-Z0-9 -]//g')
          break
        done
      elif [[ "$current_type" == "yesno" ]]; then
        while true; do
          read -rp "🔹 $current_prompt [Y/n] (default: $current_default) (enter 'd' to use default): " value
          if [[ "$value" == "d" || -z "$value" ]]; then
            value="$current_default"
          else
            value="${value,,}"  # lowercase
          fi
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
        while true; do
          read -rp "🔹 $current_prompt [$current_default] (enter 'd' to use default): " value
          [[ "$value" == "d" || -z "$value" ]] && value="$current_default"
          break
        done
      fi
      [ -z "$value" ] && value="$current_default"

      current_var=$(echo "$current_var" | xargs)
      value=$(echo "$value" | xargs)
      export "$current_var"="$value"

      # Reset current vars
      current_var=""
      current_prompt=""
      current_default=""
      current_type=""
      ;;
  esac
done < "$SETUP_FILE"