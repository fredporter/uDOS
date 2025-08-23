#!/bin/bash
# uCODE: SHOW - Display UI omniview
set -euo pipefail

CYAN='\033[0;36m'
NC='\033[0m'
UDOS_UI_PORT="8080"
UDOS_ROLE="wizard"
ui_url="http://localhost:${UDOS_UI_PORT:-8080}?role=${UDOS_ROLE:-wizard}"
echo -e "${CYAN}🌐 Opening UI: $ui_url${NC}"
case "$(uname -s)" in
    Darwin)
        open "$ui_url"
        ;;
    Linux)
        xdg-open "$ui_url" 2>/dev/null || echo "Open browser to: $ui_url"
        ;;
    *)
        echo "Open browser to: $ui_url"
        ;;
esac
