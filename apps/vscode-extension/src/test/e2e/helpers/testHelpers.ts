/**
 * E2E Test Helpers
 * Utility functions for E2E testing
 */

import * as vscode from 'vscode';
import * as sinon from 'sinon';

/**
 * Wait for a condition to be true with timeout
 */
export async function waitFor(
  condition: () => boolean,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error(`Timeout waiting for condition after ${timeout}ms`);
    }
    await sleep(interval);
  }
}

/**
 * Sleep for a specified duration
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Get the TaskMan extension
 */
export async function getTaskManExtension(): Promise<vscode.Extension<any> | undefined> {
  return vscode.extensions.getExtension('contextforge.taskman-v2-extension');
}

/**
 * Activate the TaskMan extension
 */
export async function activateExtension(): Promise<any> {
  const ext = await getTaskManExtension();
  if (!ext) {
    throw new Error('TaskMan extension not found');
  }

  if (!ext.isActive) {
    await ext.activate();
  }

  return ext.exports;
}

/**
 * Clean up after tests
 */
export function cleanupSandbox(sandbox: sinon.SinonSandbox): void {
  sandbox.restore();
}

/**
 * Create a test workspace folder
 */
export function createTestWorkspace(): vscode.WorkspaceFolder | undefined {
  const folders = vscode.workspace.workspaceFolders;
  return folders && folders.length > 0 ? folders[0] : undefined;
}

/**
 * Execute a VS Code command
 */
export async function executeCommand<T = any>(command: string, ...args: any[]): Promise<T> {
  return await vscode.commands.executeCommand<T>(command, ...args);
}

/**
 * Get configuration value
 */
export function getConfig<T>(section: string, key: string): T | undefined {
  return vscode.workspace.getConfiguration(section).get<T>(key);
}

/**
 * Set configuration value
 */
export async function setConfig(
  section: string,
  key: string,
  value: any,
  target: vscode.ConfigurationTarget = vscode.ConfigurationTarget.Workspace
): Promise<void> {
  await vscode.workspace.getConfiguration(section).update(key, value, target);
}

/**
 * Reset configuration to defaults
 */
export async function resetConfig(section: string): Promise<void> {
  const config = vscode.workspace.getConfiguration(section);
  const keys = Object.keys(config);

  for (const key of keys) {
    await config.update(key, undefined, vscode.ConfigurationTarget.Workspace);
  }
}
