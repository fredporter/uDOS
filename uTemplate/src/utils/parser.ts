/**
 * uDOS Template Parser Utilities v1.7.1
 * TypeScript utilities for parsing and processing template files
 */

export interface TemplateMetadata {
  version: string;
  template_type: string;
  created: string;
  modified: string;
  datasets: string[];
  variables: Record<string, any>;
}

export interface ParsedTemplate {
  metadata: TemplateMetadata;
  content: string;
  variables: string[];
  datasets: string[];
}

/**
 * Parse template file and extract metadata
 */
export function parseTemplate(templateContent: string): ParsedTemplate {
  const lines = templateContent.split('\n');
  let metadata: Partial<TemplateMetadata> = {};
  let content = '';
  let inMetadata = false;
  let variables: string[] = [];
  let datasets: string[] = [];

  for (const line of lines) {
    // Check for YAML front matter
    if (line.trim() === '---') {
      inMetadata = !inMetadata;
      continue;
    }

    if (inMetadata) {
      // Parse YAML-like metadata
      const match = line.match(/^(\w+):\s*(.+)$/);
      if (match) {
        const [, key, value] = match;
        metadata[key as keyof TemplateMetadata] = value.trim();
      }
    } else {
      content += line + '\n';
      
      // Extract template variables {{variable}}
      const varMatches = line.match(/\{\{([^}]+)\}\}/g);
      if (varMatches) {
        varMatches.forEach(match => {
          const variable = match.replace(/[{}]/g, '').trim();
          if (!variables.includes(variable)) {
            variables.push(variable);
          }
        });
      }
      
      // Extract dataset references
      const datasetMatches = line.match(/dataset:\s*(\w+)/g);
      if (datasetMatches) {
        datasetMatches.forEach(match => {
          const dataset = match.replace('dataset:', '').trim();
          if (!datasets.includes(dataset)) {
            datasets.push(dataset);
          }
        });
      }
    }
  }

  return {
    metadata: metadata as TemplateMetadata,
    content: content.trim(),
    variables,
    datasets
  };
}

/**
 * Replace template variables with actual values
 */
export function renderTemplate(
  template: string, 
  variables: Record<string, any>
): string {
  let rendered = template;
  
  Object.entries(variables).forEach(([key, value]) => {
    const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
    rendered = rendered.replace(regex, String(value));
  });
  
  return rendered;
}

/**
 * Extract coordinate references from template content
 */
export function extractCoordinates(content: string): string[] {
  const coordinates: string[] = [];
  const coordPattern = /([A-Z]{1,2}\d{1,2})/g;
  
  let match;
  while ((match = coordPattern.exec(content)) !== null) {
    if (!coordinates.includes(match[1])) {
      coordinates.push(match[1]);
    }
  }
  
  return coordinates;
}

/**
 * Validate template against schema
 */
export function validateTemplate(parsed: ParsedTemplate): string[] {
  const errors: string[] = [];
  
  if (!parsed.metadata.version) {
    errors.push('Missing template version');
  }
  
  if (!parsed.metadata.template_type) {
    errors.push('Missing template type');
  }
  
  if (parsed.variables.length === 0) {
    errors.push('No template variables found');
  }
  
  return errors;
}

/**
 * Generate template summary
 */
export function generateTemplateSummary(parsed: ParsedTemplate): string {
  return `
Template Summary:
- Type: ${parsed.metadata.template_type || 'Unknown'}
- Version: ${parsed.metadata.version || 'Unknown'}
- Variables: ${parsed.variables.length}
- Datasets: ${parsed.datasets.length}
- Content Length: ${parsed.content.length} characters
`;
}