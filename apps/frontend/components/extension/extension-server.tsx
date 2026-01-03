import { useState, useEffect } from 'react';
import { useKV } from '@github/spark/hooks';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Download, Copy, Code } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { useApiServer, generateCurlExamples } from './api-server';

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
  metadata: string;
  apiEndpoints: {
    metadata: string;
    download: string;
  };
}

export default function ExtensionServer() {
  const [extensions, setExtensions] = useKV<ExtensionData[]>('extensions', []);
  const [selectedExtension, setSelectedExtension] = useState<ExtensionData | null>(null);
  const apiHandlers = useApiServer();

  const baseUrl = window.location.origin;

  // Initialize with sample data if empty
  useEffect(() => {
    if (!extensions || extensions.length === 0) {
      const sampleExtensions: ExtensionData[] = [
        {
          info: {
            name: 'vscode-todos',
            displayName: 'VS Code TODOs',
            description: 'Highlight and manage TODO comments in your code',
            version: '1.2.3',
            publisher: 'example-publisher',
            categories: ['Programming Languages', 'Other'],
            keywords: ['todo', 'comments', 'productivity', 'tasks'],
            repository: {
              type: 'git',
              url: 'https://github.com/example/vscode-todos'
            },
            bugs: {
              url: 'https://github.com/example/vscode-todos/issues'
            },
            homepage: 'https://github.com/example/vscode-todos'
          },
          downloadUrl: `${baseUrl}/extensions/vscode-todos-1.2.3.vsix`,
          installCommand: 'code --install-extension vscode-todos-1.2.3.vsix',
          metadata: JSON.stringify({
            name: 'vscode-todos',
            version: '1.2.3',
            publisher: 'example-publisher',
            description: 'Highlight and manage TODO comments in your code',
            categories: ['Programming Languages', 'Other'],
            keywords: ['todo', 'comments', 'productivity', 'tasks']
          }, null, 2),
          apiEndpoints: {
            metadata: `${baseUrl}/api/extensions/vscode-todos`,
            download: `${baseUrl}/api/extensions/vscode-todos/download`
          }
        }
      ];
      setExtensions(sampleExtensions);
    }
  }, [extensions, setExtensions, baseUrl]);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${label} copied to clipboard!`);
    } catch (err) {
      toast.error('Failed to copy to clipboard');
    }
  };

  const handleDownload = (extension: ExtensionData) => {
    const link = document.createElement('a');
    link.href = extension.downloadUrl;
    link.download = `${extension.info.name}-${extension.info.version}.vsix`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">VS Code Extension Server</h1>
          <p className="text-muted-foreground text-lg">
            Manage and distribute custom VS Code extensions with GitHub Copilot Agent integration
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Extension List */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Available Extensions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {extensions && extensions.length > 0 ? (
                    extensions.map((extension) => (
                      <div
                        key={extension.info.name}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors hover:bg-accent ${
                          selectedExtension?.info.name === extension.info.name ? 'bg-accent' : ''
                        }`}
                        onClick={() => setSelectedExtension(extension)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="min-w-0 flex-1">
                            <h4 className="font-medium truncate">{extension.info.displayName}</h4>
                            <p className="text-sm text-muted-foreground">
                              {extension.info.publisher} • v{extension.info.version}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {extension.info.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-muted-foreground">
                      No extensions available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Extension Details */}
          <div className="lg:col-span-2">
            {selectedExtension ? (
              <Card>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-xl">{selectedExtension.info.displayName}</CardTitle>
                      <CardDescription className="mt-2">
                        {selectedExtension.info.description}
                      </CardDescription>
                      <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                        <span>{selectedExtension.info.publisher}</span>
                        <span>v{selectedExtension.info.version}</span>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleDownload(selectedExtension)}
                      className="shrink-0"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Categories Section */}
                    <div>
                      <h3 className="font-semibold mb-2">Categories</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedExtension.info.categories.map((category) => (
                          <Badge key={category} variant="outline">
                            {category}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Keywords Section */}
                    <div>
                      <h3 className="font-semibold mb-2">Keywords</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedExtension.info.keywords.map((keyword) => (
                          <Badge key={keyword} variant="secondary">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Installation Command */}
                    <div>
                      <h3 className="font-semibold mb-2">Installation Command</h3>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 p-2 bg-muted rounded text-sm font-mono">
                          {selectedExtension.installCommand}
                        </code>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(selectedExtension.installCommand, 'Install command')}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>


                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-8">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold">Select an Extension</h3>
                    <p className="text-muted-foreground mt-2">
                      Choose an extension from the list to view details and installation instructions.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
