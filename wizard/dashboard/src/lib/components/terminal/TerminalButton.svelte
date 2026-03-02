<script>
  export let label = "Button";
  export let onClick = () => {};
  export let disabled = false;
  export let variant = "primary"; // "primary" | "secondary" | "danger"

  const handleClick = () => {
    if (!disabled) {
      onClick();
    }
  };

  const baseStyle = "padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; transition: all 0.2s;";
  const primaryStyle = `${baseStyle} background: #3b82f6; color: white; hover: background: #2563eb;`;
  const secondaryStyle = `${baseStyle} background: #64748b; color: white;`;
  const dangerStyle = `${baseStyle} background: #ef4444; color: white;`;
  const disabledStyle = `${baseStyle} opacity: 0.5; cursor: not-allowed;`;

  let finalStyle = baseStyle;
  $: {
    if (disabled) {
      finalStyle = disabledStyle;
    } else if (variant === "danger") {
      finalStyle = dangerStyle;
    } else if (variant === "secondary") {
      finalStyle = secondaryStyle;
    } else {
      finalStyle = primaryStyle;
    }
  }
</script>

<button {disabled} on:click={handleClick} style={finalStyle}>
  {label}
</button>
