import { http, HttpResponse } from 'msw';

// Mock API handlers for testing
export const testHandlers = [
  // Extension API endpoints
  http.get('/api/extensions', () => {
    return HttpResponse.json([
      {
        name: 'dynamic-task-manager',
        displayName: 'Dynamic Task Manager',
        version: '1.0.0',
        publisher: 'test-publisher',
        description: 'A VS Code extension for managing tasks dynamically'
      }
    ]);
  }),

  http.get('/api/extensions/:extensionId', ({ params }) => {
    const { extensionId } = params;
    return HttpResponse.json({
      name: extensionId,
      displayName: 'Dynamic Task Manager',
      version: '1.0.0',
      publisher: 'test-publisher',
      description: 'A VS Code extension for managing tasks dynamically',
      categories: ['Programming Languages', 'Other'],
      keywords: ['tasks', 'productivity', 'vscode']
    });
  }),

  http.get('/api/extensions/:extensionId/download', ({ params }) => {
    const { extensionId } = params;
    return HttpResponse.text(`Mock VSIX content for ${extensionId}`, {
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${extensionId}.vsix"`
      }
    });
  }),

  // Health check endpoint
  http.get('/api/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: Date.now(),
      version: '1.0.0'
    });
  }),

  // Extension upload endpoint
  http.post('/api/extensions/upload', () => {
    return HttpResponse.json({
      success: true,
      extensionId: 'uploaded-extension',
      message: 'Extension uploaded successfully'
    });
  }),

  // Extension validation endpoint
  http.post('/api/extensions/validate', () => {
    return HttpResponse.json({
      valid: true,
      metadata: {
        name: 'test-extension',
        version: '1.0.0',
        publisher: 'test-publisher'
      }
    });
  })
];