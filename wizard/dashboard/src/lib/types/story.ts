/**
 * Story Format Type Definitions
 * 
 * Defines the structure for -story.md files:
 * - Single-file, distributable markdown documents
 * - Interactive typeform-style Q&A between sections
 * - Variable/object collection and management
 * - Sandboxed execution (no external runtime access)
 */

export interface StoryFrontmatter {
  title: string;
  type: 'story';
  version: string;
  description?: string;
  author?: string;
  created?: string;
  tags?: string[];
  variables?: Record<string, any>;
  sections?: StorySection[];
  submit_endpoint?: string;
  submit_requires_admin?: boolean;
}

export interface StorySection {
  id: string;
  title: string;
  content: string; // Markdown prose content
  questions: FormField[];
  order: number;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'select' | 'checkbox' | 'radio' | 'textarea' | 'location';
  required?: boolean;
  placeholder?: string;
  options?: string[]; // For select/radio
  value?: any;
  meta?: Record<string, any>;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    custom?: (value: any) => boolean;
  };
}

export interface StoryState {
  frontmatter: StoryFrontmatter;
  sections: StorySection[];
  currentSectionIndex: number;
  answers: Record<string, any>;
  isComplete: boolean;
}

export interface StoryRendererProps {
  story: StoryState;
  onSubmit?: (answers: Record<string, any>) => void;
  onSectionChange?: (sectionIndex: number) => void;
  onReset?: () => void;
  showProgress?: boolean;
  theme?: 'light' | 'dark' | 'auto';
}
