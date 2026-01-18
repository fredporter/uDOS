/**
 * FormExecutor - Render and handle form input
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult, FormField } from '../types'
import { BaseExecutor } from './base'

export class FormExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const fields = this.parseFormFields(block.content)

      // In a real implementation, this would render the form UI
      // and capture user input. For now, we'll just return the structure.
      const output = this.renderForm(fields)

      return {
        success: true,
        output,
        formFields: fields,
      } as any
    } catch (error) {
      return {
        success: false,
        error: `FormExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private parseFormFields(content: string): FormField[] {
    const fields: FormField[] = []
    const lines = content.split('\n')
    
    // Detect format: blank-line-separated or indented-properties
    const hasBlankLineSeparators = /\n\s*\n/.test(content)
    const hasIndentedKeys = /\n\s{2,}/.test(content)
    
    if (hasBlankLineSeparators && !hasIndentedKeys) {
      // Format 1: Blank-line separated blocks
      return this.parseBlankLineSeparatedFields(content)
    } else if (hasIndentedKeys) {
      // Format 2: Indented properties (name-first)
      return this.parseIndentedFields(lines)
    } else {
      // Format 3: Simple flat format
      return this.parseFlatFields(lines)
    }
  }

  private parseBlankLineSeparatedFields(content: string): FormField[] {
    const fields: FormField[] = []
    const blocks = content.split(/\n\s*\n/)

    for (const block of blocks) {
      if (!block.trim()) continue

      const field: any = {}
      const lines = block.trim().split('\n')

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) continue

        if (trimmed.includes(':')) {
          const colonIndex = trimmed.indexOf(':')
          const key = trimmed.substring(0, colonIndex).trim()
          const value = trimmed.substring(colonIndex + 1).trim()

          if (key === 'field') field.type = value
          if (key === 'var') field.var = value
          if (key === 'label') field.label = value.replace(/^"|"$/g, '')
          if (key === 'type') field.type = value
          if (key === 'required') field.required = value === 'true'
          if (key === 'placeholder') field.placeholder = value.replace(/^"|"$/g, '')
          if (key === 'default') field.default = value
          if (key === 'pattern') field.pattern = value
          if (key === 'options') {
            try {
              // eslint-disable-next-line no-eval
              field.options = eval(`(${value})`)
            } catch {
              field.options = value
            }
          }
        }
      }

      if (field.type || field.var) {
        fields.push(field)
      }
    }

    return fields
  }

  private parseIndentedFields(lines: string[]): FormField[] {
    const fields: FormField[] = []
    let currentField: any = null

    for (const line of lines) {
      const trimmed = line.trim()
      const isIndented = line.startsWith('  ') || line.startsWith('\t')

      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) {
        continue
      }

      if (trimmed.includes(':')) {
        const colonIndex = trimmed.indexOf(':')
        const key = trimmed.substring(0, colonIndex).trim()
        const value = trimmed.substring(colonIndex + 1).trim()

        if (!isIndented) {
          // Non-indented = new field definition (e.g., "username: Label")
          if (currentField && (currentField.var || currentField.type)) {
            fields.push(currentField)
          }
          currentField = { var: key, label: value.replace(/^"|"$/g, '') }
        } else if (currentField) {
          // Indented = property of current field
          if (key === 'type') currentField.type = value
          if (key === 'required') currentField.required = value === 'true'
          if (key === 'placeholder') currentField.placeholder = value.replace(/^"|"$/g, '')
          if (key === 'default') currentField.default = value
          if (key === 'pattern') currentField.pattern = value
          if (key === 'options') {
            try {
              // eslint-disable-next-line no-eval
              currentField.options = eval(`(${value})`)
            } catch {
              currentField.options = value
            }
          }
        }
      }
    }

    if (currentField && (currentField.var || currentField.type)) {
      fields.push(currentField)
    }

    return fields
  }

  private parseFlatFields(lines: string[]): FormField[] {
    const fields: FormField[] = []
    const field: any = {}

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) continue

      if (trimmed.includes(':')) {
        const colonIndex = trimmed.indexOf(':')
        const key = trimmed.substring(0, colonIndex).trim()
        const value = trimmed.substring(colonIndex + 1).trim()

        if (key === 'field') field.type = value
        if (key === 'var') field.var = value
        if (key === 'label') field.label = value.replace(/^"|"$/g, '')
        if (key === 'type') field.type = value
        if (key === 'required') field.required = value === 'true'
        if (key === 'placeholder') field.placeholder = value.replace(/^"|"$/g, '')
        if (key === 'default') field.default = value
        if (key === 'pattern') field.pattern = value
        if (key === 'options') {
          try {
            // eslint-disable-next-line no-eval
            field.options = eval(`(${value})`)
          } catch {
            field.options = value
          }
        }
      }
    }

    if (field.type || field.var) {
      fields.push(field)
    }

    return fields
  }

  private renderForm(fields: FormField[]): string {
    let output = '┌' + '─'.repeat(40) + '┐\n'
    output += '│ Form Input                            │\n'
    output += '├' + '─'.repeat(40) + '┤\n'

    for (const field of fields) {
      const label = field.label || field.var
      const req = field.required ? '*' : ''
      output += `│ ${label.padEnd(35)}${req} │\n`
    }

    output += '└' + '─'.repeat(40) + '┘\n'

    return output
  }
}
