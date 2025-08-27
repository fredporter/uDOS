# Test Conditional Template

## User Information
- **Role**: {USER-ROLE}
- **Level**: {USER-LEVEL}

{#if DEV-MODE}
## Development Mode Active
- Debug level is active
- Development tools available
{/if}

## Always Visible
This content is always shown.

{#if USER-LEVEL}
## User Level Content
Your level is: {USER-LEVEL}
{/if}

End of template.
