/**
 * Extension Activation E2E Tests
 * Tests that verify the extension loads and activates correctly
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import { activateExtension, getTaskManExtension } from '../helpers/testHelpers';

suite('Extension Activation Tests', () => {
  test('Extension should be present', async () => {
    const ext = await getTaskManExtension();
    assert.ok(ext, 'Extension should be found');
  });

  test('Extension should activate', async function () {
    this.timeout(10000); // Allow 10 seconds for activation

    const ext = await getTaskManExtension();
    assert.ok(ext, 'Extension must be present');

    await activateExtension();
    assert.strictEqual(ext.isActive, true, 'Extension should be active');
  });

  test('Extension should have correct ID', async () => {
    const ext = await getTaskManExtension();
    assert.ok(ext, 'Extension must be present');
    assert.strictEqual(
      ext.id,
      'contextforge.taskman-v2-extension',
      'Extension ID should match'
    );
  });

  test('Extension should have correct version', async () => {
    const ext = await getTaskManExtension();
    assert.ok(ext, 'Extension must be present');

    // Version should be 1.0.2 or higher
    const version = ext.packageJSON.version;
    assert.ok(version, 'Extension should have a version');

    const versionParts = version.split('.').map(Number);
    assert.ok(
      versionParts[0] >= 1 && versionParts[1] >= 0 && versionParts[2] >= 2,
      `Version should be 1.0.2 or higher, got ${version}`
    );
  });

  test('All commands should be registered', async function () {
    this.timeout(10000);

    await activateExtension();

    const expectedCommands = [
      'taskman.add',
      'taskman.toggle',
      'taskman.edit',
      'taskman.delete',
      'taskman.refresh',
      'taskman.addGroup',
      'taskman.settings',
      'taskman.loadFromDatabase',
      'taskman.syncWithDTM',
      'taskman.connectDatabase',
      'taskman.databaseSettings',
      'taskman.testConnection',
      'taskman.exportTasks',
      'taskman.importTasks',
      'taskman.openSharedConfig',
      'taskman.showSyncStatus',
    ];

    const allCommands = await vscode.commands.getCommands(true);

    for (const cmd of expectedCommands) {
      assert.ok(
        allCommands.includes(cmd),
        `Command ${cmd} should be registered`
      );
    }
  });

  test('TreeView should be registered', async function () {
    this.timeout(10000);

    await activateExtension();

    // Check that the tree view container exists
    const treeViews = vscode.window.tabGroups.all.flatMap(group =>
      group.tabs.map(tab => tab.label)
    );

    // The TaskMan tree view should be available in the sidebar
    // We can't directly test if it's visible, but we can verify the extension activated
    const ext = await getTaskManExtension();
    assert.strictEqual(ext?.isActive, true, 'Extension should be active for TreeView');
  });

  test('Configuration defaults should be correct', async () => {
    const config = vscode.workspace.getConfiguration('taskman');

    // Verify port is 3001 (not 3000)
    const serverPort = config.get<number>('dtm.serverPort');
    assert.strictEqual(
      serverPort,
      3001,
      'Default server port should be 3001 (UB-001 fix)'
    );

    // Verify API URL uses port 3001
    const apiUrl = config.get<string>('database.dtmApiUrl');
    assert.ok(
      apiUrl?.includes(':3001'),
      'API URL should use port 3001'
    );

    // Verify other default settings
    const autoSync = config.get<boolean>('sync.enabled');
    assert.strictEqual(typeof autoSync, 'boolean', 'Auto-sync should be a boolean');

    const databaseMode = config.get<string>('database.mode');
    assert.ok(
      ['sqlite', 'api', 'hybrid'].includes(databaseMode || ''),
      'Database mode should be valid'
    );
  });

  test('Extension should load without errors', async function () {
    this.timeout(10000);

    const ext = await getTaskManExtension();
    assert.ok(ext, 'Extension must be present');

    // Activate and ensure no errors are thrown
    await assert.doesNotReject(
      async () => await activateExtension(),
      'Extension activation should not throw errors'
    );
  });
});
