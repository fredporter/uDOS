# Form Example

This is an example of a Typeform-style form defined in markdown.

```yaml
form:
  title: uDOS Feedback Survey
  description: Help us improve uDOS
  submitLabel: Submit Feedback
  questions:
    - type: text
      label: What is your name?
      placeholder: Your name
      required: true
    - type: email
      label: What is your email address?
      description: We'll never share your email with anyone.
      placeholder: you@example.com
      required: true
    - type: select
      label: How did you discover uDOS?
      options: [GitHub, Friend, Search Engine, Social Media, Other]
      required: true
    - type: rating
      label: How would you rate your overall experience?
      description: 1 = Poor, 5 = Excellent
      min: 1
      max: 5
      required: true
    - type: multiselect
      label: Which features do you use most?
      options: [Desktop, Typo Editor, Terminal, Knowledge Bank, Teledesk]
    - type: textarea
      label: Any suggestions for improvement?
      placeholder: Tell us what you think...
    - type: select
      label: Would you recommend uDOS to others?
      options: [Definitely, Probably, Not sure, Probably not]
      required: true
```

## How to use

1. Create a markdown file with the form definition above
2. Open it in Desktop file viewer
3. Click the "Form" button to launch the interactive form
4. Submit responses which are saved to memory/forms/

## Supported question types

- **text**: Single line text input
- **email**: Email input with validation
- **number**: Numeric input with min/max
- **select**: Single choice from options
- **multiselect**: Multiple choice from options
- **textarea**: Multi-line text input
- **rating**: Numeric rating scale
