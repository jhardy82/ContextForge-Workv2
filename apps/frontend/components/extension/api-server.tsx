import { useEffect } from 'react';
import { useKV } from '@github/spark/hooks';

interface ExtensionInfo {
  name: string;
  displayName: string;
  description: string;
  version: string;
  publisher: string;
  categories: string[];
  keywords: string[];
  repository?: {
    type: string;
    url: string;
  };
  bugs?: {
    url: string;
  };
  homepage?: string;
}

interface ExtensionData {
  info: ExtensionInfo;
  downloadUrl: string;
  installCommand: string;
  apiEndpoints: {
    metadata: string;
    download: string;
  };
}

// This simulates API endpoints that would normally be served by a backend
// In a real implementation, these would be actual HTTP endpoints
export const useApiServer = () => {
  const [extensions] = useKV<ExtensionData[]>('extensions', []);

  // Simulate API endpoints for GitHub Copilot Agent integration
  const apiHandlers = {
    // GET /api/extensions - List all extensions
    getExtensions: () => {
      return {
        extensions: extensions?.map(ext => ({
          name: ext.info.name,
          displayName: ext.info.displayName,
          version: ext.info.version,
          publisher: ext.info.publisher,
          description: ext.info.description,
          categories: ext.info.categories,
          keywords: ext.info.keywords,
          downloadUrl: ext.downloadUrl,
          installCommand: ext.installCommand
        })) || []
      };
    },

    // GET /api/extensions/:name - Get specific extension metadata
    getExtension: (name: string) => {
      const extension = extensions?.find(ext => ext.info.name === name);
      if (!extension) {
        return { error: 'Extension not found', status: 404 };
      }
      
      return {
        name: extension.info.name,
        displayName: extension.info.displayName,
        version: extension.info.version,
        publisher: extension.info.publisher,
        description: extension.info.description,
        categories: extension.info.categories,
        keywords: extension.info.keywords,
        repository: extension.info.repository,
        bugs: extension.info.bugs,
        homepage: extension.info.homepage,
        downloadUrl: extension.downloadUrl,
        installCommand: extension.installCommand,
        apiEndpoints: extension.apiEndpoints
      };
    },

    // GET /api/extensions/:name/download - Download extension file
    downloadExtension: (name: string) => {
      const extension = extensions?.find(ext => ext.info.name === name);
      if (!extension) {
        return { error: 'Extension not found', status: 404 };
      }
      
      // In a real implementation, this would stream the .vsix file
      return {
        filename: `${name}-${extension.info.version}.vsix`,
        contentType: 'application/octet-stream',
        size: 1024000, // Simulated file size
        downloadUrl: extension.downloadUrl
      };
    },

    // GitHub Copilot Agent specific endpoint
    // GET /api/copilot/extensions - Optimized for agent consumption
    getCopilotExtensions: () => {
      return {
        version: '1.0',
        server: 'VS Code Extension Server',
        extensions: extensions?.map(ext => ({
          id: ext.info.name,
          name: ext.info.displayName,
          version: ext.info.version,
          publisher: ext.info.publisher,
          description: ext.info.description,
          installCommand: ext.installCommand,
          directDownload: ext.downloadUrl,
          categories: ext.info.categories,
          keywords: ext.info.keywords
        })) || [],
        installInstructions: {
          vscode: 'Use the VS Code CLI: code --install-extension <downloadUrl>',
          manual: 'Download the .vsix file and install via VS Code Extensions view'
        }
      };
    }
  };

  // Simulate setting up global API handlers that GitHub Copilot Agent could access
  useEffect(() => {
    // In a real implementation, these would be actual HTTP endpoints
    // For demonstration, we're storing them on the window object
    (window as any).extensionServerAPI = apiHandlers;
    
    // Log available endpoints for debugging
    console.log('Extension Server API endpoints available:', {
      'GET /api/extensions': 'List all extensions',
      'GET /api/extensions/:name': 'Get specific extension metadata',
      'GET /api/extensions/:name/download': 'Download extension file',
      'GET /api/copilot/extensions': 'GitHub Copilot Agent optimized endpoint'
    });
  }, [extensions]);

  return apiHandlers;
};

// Utility function to generate curl examples for API documentation
export const generateCurlExamples = (baseUrl: string) => {
  return {
    listExtensions: `curl -X GET "${baseUrl}/api/extensions"`,
    getExtension: `curl -X GET "${baseUrl}/api/extensions/vscode-todos"`,
    downloadExtension: `curl -X GET -o extension.vsix "${baseUrl}/api/extensions/vscode-todos/download"`,
    copilotEndpoint: `curl -X GET -H "Authorization: Bearer <token>" "${baseUrl}/api/copilot/extensions"`
  };
};

// Helper function for GitHub Copilot Agent integration
export const getCopilotCompatibleResponse = (extensions: ExtensionData[]) => {
  return {
    type: 'extension_registry',
    version: '1.0',
    server_info: {
      name: 'VS Code Extension Server',
      description: 'Serves custom VS Code extensions for development environments'
    },
    extensions: extensions.map(ext => ({
      identifier: ext.info.name,
      display_name: ext.info.displayName,
      version: ext.info.version,
      publisher: ext.info.publisher,
      description: ext.info.description,
      install_methods: [
        {
          method: 'vscode_cli',
          command: ext.installCommand,
          description: 'Install using VS Code CLI'
        },
        {
          method: 'direct_download',
          url: ext.downloadUrl,
          description: 'Download .vsix file directly'
        }
      ],
      metadata: {
        categories: ext.info.categories,
        keywords: ext.info.keywords,
        repository: ext.info.repository,
        homepage: ext.info.homepage
      }
    })),
    usage_instructions: {
      vscode_installation: 'Use "code --install-extension <url>" to install',
      manual_installation: 'Download .vsix file and install through VS Code Extensions panel',
      copilot_integration: 'This registry is compatible with GitHub Copilot Agent for automated extension recommendations'
    }
  };
};