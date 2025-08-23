BLUE='\033[0;34m'
NC='\033[0m'
#!/bin/bash
# uCODE: TREE - Show directory tree for system, user, or install
set -euo pipefail


UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
target="${1:-$UDOS_ROOT}"

echo "${BLUE}📂 Directory Tree for: $target${NC}"
tree_cmd="tree"
if ! command -v tree >/dev/null 2>&1; then
    # Custom tree fallback, formats with branches and hides .git/.vscode
    find "$target" \( -name ".git" -o -name ".vscode" \) -prune -o -print | \
    sed -e "s|^$target||" -e '/^$/d' | \
    awk -F'/' '{
        indent = "";
        for (i=2; i<NF; i++) indent = indent "   ";
        branch = (NF>1 ? "|-- " : "");
        print indent branch $NF
    }'
    exit 0
fi
$tree_cmd --dirsfirst -I ".git|.vscode" "$target"
