/**
 * Settings and Configuration E2E Tests
 * Tests configuration management and settings validation
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import { activateExtension, getConfig, setConfig, resetConfig } from '../helpers/testHelpers';

suite('Settings and Configuration Tests', () => {
  const CONFIG_SECTION = 'taskman';

  suiteSetup(async function () {
    this.timeout(15000);
    await activateExtension();
  });

  suiteTeardown(async () => {
    // Reset configuration after all tests
    await resetConfig(CONFIG_SECTION);
  });

  test('Default port should be 3001 (UB-001 fix verification)', () => {
    const port = getConfig<number>(CONFIG_SECTION, 'dtm.serverPort');
    assert.strictEqual(
      port,
      3001,
      'Default DTM server port should be 3001 (not 3000)'
    );
  });

  test('Default API URL should use port 3001', () => {
    const apiUrl = getConfig<string>(CONFIG_SECTION, 'database.dtmApiUrl');

    assert.ok(apiUrl, 'API URL should be defined');
    assert.ok(
      apiUrl.includes('3001'),
      'API URL should include port 3001'
    );
    assert.ok(
      apiUrl.includes('localhost'),
      'API URL should use localhost by default'
    );
    assert.ok(
      apiUrl.includes('/api'),
      'API URL should include /api path'
    );
  });

  test('Database mode configuration should have valid default', () => {
    const mode = getConfig<string>(CONFIG_SECTION, 'database.mode');

    assert.ok(mode, 'Database mode should be defined');
    assert.ok(
      ['sqlite', 'api', 'hybrid'].includes(mode),
      `Database mode should be one of: sqlite, api, hybrid. Got: ${mode}`
    );
  });

  test('Sync configuration should have boolean enabled flag', () => {
    const enabled = getConfig<boolean>(CONFIG_SECTION, 'sync.enabled');

    assert.strictEqual(
      typeof enabled,
      'boolean',
      'Sync enabled should be a boolean'
    );
  });

  test('Sync interval should be a positive number', () => {
    const interval = getConfig<number>(CONFIG_SECTION, 'sync.intervalSeconds');

    if (interval !== undefined) {
      assert.ok(
        typeof interval === 'number' && interval > 0,
        'Sync interval should be a positive number'
      );
    }
  });

  test('Should have database settings command', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('taskman.databaseSettings'),
      'Database settings command should be registered'
    );
  });

  test('Should have general settings command', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('taskman.settings'),
      'General settings command should be registered'
    );
  });

  test('Should have test connection command', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('taskman.testConnection'),
      'Test connection command should be registered'
    );
  });

  test('Should have connect database command', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('taskman.connectDatabase'),
      'Connect database command should be registered'
    );
  });

  test('Should have open shared config command', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('taskman.openSharedConfig'),
      'Open shared config command should be registered'
    );
  });

  test('Configuration should be modifiable at runtime', async function () {
    this.timeout(10000);

    const originalPort = getConfig<number>(CONFIG_SECTION, 'dtm.serverPort');

    // Try to set a new port
    await setConfig(CONFIG_SECTION, 'dtm.serverPort', 3002);

    const newPort = getConfig<number>(CONFIG_SECTION, 'dtm.serverPort');
    assert.strictEqual(newPort, 3002, 'Port should be updated to 3002');

    // Restore original value
    await setConfig(CONFIG_SECTION, 'dtm.serverPort', originalPort);

    const restoredPort = getConfig<number>(CONFIG_SECTION, 'dtm.serverPort');
    assert.strictEqual(
      restoredPort,
      originalPort,
      'Port should be restored to original value'
    );
  });

  test('Invalid configuration should be handled gracefully', () => {
    // Test that getting a non-existent config returns undefined
    const nonExistent = getConfig<string>(CONFIG_SECTION, 'nonexistent.config.key');

    assert.strictEqual(
      nonExistent,
      undefined,
      'Non-existent config should return undefined'
    );
  });
});
