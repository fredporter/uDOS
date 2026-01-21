/**
 * Typo File Operations - Tauri Backend Integration
 * Provides file operations integrated with uDOS file system
 */

import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { open, save } from '@tauri-apps/plugin-dialog';

export interface FileInfo {
  path: string;
  name: string;
  exists: boolean;
}

export interface FileOperations {
  // File I/O
  readFile: (path: string) => Promise<string>;
  writeFile: (path: string, content: string) => Promise<void>;
  
  // File management
  createNew: (workspace: string, filename?: string) => Promise<FileInfo>;
  rename: (oldPath: string, newName: string) => Promise<FileInfo>;
  duplicate: (path: string, newName?: string) => Promise<FileInfo>;
  moveTo: (path: string, workspace: string) => Promise<FileInfo>;
  
  // Utilities
  getWorkspaces: () => Promise<string[]>;
  getDefaultReadme: () => Promise<string>;
  
  // Dialog operations
  openFileDialog: () => Promise<string | null>;
  saveFileDialog: (defaultName?: string) => Promise<string | null>;
}

/**
 * Read a markdown file
 */
export async function readMarkdownFile(path: string): Promise<string> {
  try {
    return await invoke<string>('read_markdown_file', { path });
  } catch (error) {
    console.error('[Typo] Failed to read file:', error);
    throw new Error(`Failed to read file: ${error}`);
  }
}

/**
 * Write content to a markdown file
 */
export async function writeMarkdownFile(path: string, content: string): Promise<void> {
  try {
    await invoke('write_markdown_file', { path, content });
  } catch (error) {
    console.error('[Typo] Failed to write file:', error);
    throw new Error(`Failed to write file: ${error}`);
  }
}

/**
 * Create a new file in specified uDOS workspace
 */
export async function createNewFile(workspace: string, filename?: string): Promise<FileInfo> {
  try {
    return await invoke<FileInfo>('create_new_file', { workspace, filename });
  } catch (error) {
    console.error('[Typo] Failed to create file:', error);
    throw new Error(`Failed to create file: ${error}`);
  }
}

/**
 * Rename a file
 */
export async function renameFile(oldPath: string, newName: string): Promise<FileInfo> {
  try {
    return await invoke<FileInfo>('rename_file', { oldPath, newName });
  } catch (error) {
    console.error('[Typo] Failed to rename file:', error);
    throw new Error(`Failed to rename file: ${error}`);
  }
}

/**
 * Duplicate a file
 */
export async function duplicateFile(path: string, newName?: string): Promise<FileInfo> {
  try {
    return await invoke<FileInfo>('duplicate_file', { path, newName });
  } catch (error) {
    console.error('[Typo] Failed to duplicate file:', error);
    throw new Error(`Failed to duplicate file: ${error}`);
  }
}

/**
 * Move file to different workspace
 */
export async function moveFile(fromPath: string, toWorkspace: string): Promise<FileInfo> {
  try {
    return await invoke<FileInfo>('move_file', { fromPath, toWorkspace });
  } catch (error) {
    console.error('[Typo] Failed to move file:', error);
    throw new Error(`Failed to move file: ${error}`);
  }
}

/**
 * Get list of available uDOS workspaces
 */
export async function getUdosWorkspaces(): Promise<string[]> {
  try {
    return await invoke<string[]>('get_udos_workspaces');
  } catch (error) {
    console.error('[Typo] Failed to get workspaces:', error);
    return ['sandbox', 'drafts', 'user', 'private', 'shared'];
  }
}

/**
 * Get path to default readme file
 */
export async function getDefaultReadmePath(): Promise<string> {
  try {
    return await invoke<string>('get_default_readme_path');
  } catch (error) {
    console.error('[Typo] Failed to get default readme:', error);
    throw error;
  }
}

/**
 * Open file dialog
 */
export async function openFileDialog(): Promise<string | null> {
  try {
    const selected = await open({
      multiple: false,
      directory: false,
      filters: [{
        name: 'Markdown',
        extensions: ['md', 'markdown', 'mdx', 'txt']
      }]
    });
    
    return selected as string | null;
  } catch (error) {
    console.error('[Typo] Failed to open file dialog:', error);
    return null;
  }
}

/**
 * Save file dialog
 */
export async function saveFileDialog(defaultName?: string): Promise<string | null> {
  try {
    const selected = await save({
      defaultPath: defaultName,
      filters: [{
        name: 'Markdown',
        extensions: ['md']
      }]
    });
    
    return selected as string | null;
  } catch (error) {
    console.error('[Typo] Failed to open save dialog:', error);
    return null;
  }
}

/**
 * Listen for menu events from native menu
 */
export async function listenToMenuEvents(handler: (menuId: string) => void) {
  await listen<string>('menu-event', (event) => {
    handler(event.payload);
  });
}

/**
 * Listen for file open events (from command line or uDOS)
 */
export async function listenToFileOpen(handler: (filepath: string) => void) {
  await listen<string>('open-file', (event) => {
    handler(event.payload);
  });
}

// Export all functions as a convenience object
export const fileOps: FileOperations = {
  readFile: readMarkdownFile,
  writeFile: writeMarkdownFile,
  createNew: createNewFile,
  rename: renameFile,
  duplicate: duplicateFile,
  moveTo: moveFile,
  getWorkspaces: getUdosWorkspaces,
  getDefaultReadme: getDefaultReadmePath,
  openFileDialog,
  saveFileDialog,
};

export default fileOps;
