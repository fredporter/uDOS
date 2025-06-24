# Main command dispatch loop
case "${1^^}" in
  # ... (other command cases go here)

  BYE)
    echo "👋 uDOS is now entering shutdown mode..."
    echo "🔒 Session is idle. You can type:"
    echo "   [R] RESTART → Soft refresh"
    echo "   [B] REBOOT  → Full setup and check"
    echo "   [D] DESTROY → Delete your identity"
    echo "   [C] CANCEL  → Return to CLI"
    read -n1 -rp "👉 Choose next step: " next
    echo ""
    case "${next^^}" in
      R) $0 RESTART ;;
      B) $0 REBOOT ;;
      D) $0 DESTROY ;;
      *) echo "🌀 Returning to CLI..." ;;
    esac
    ;;

  EXIT)
    $0 BYE
    ;;

  QUIT)
    $0 BYE
    ;;

  *)
    echo "🧠 Available uDOS commands:"
    echo "   NEW       → Create new item"
    echo "   RUN       → Start current item"
    echo "   LOG       → Save progress"
    echo "   UNDO      → Reverse last move"
    echo "   EXIT/QUIT → Close session"
    ;;
esac