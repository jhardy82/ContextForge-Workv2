import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  console.log("Starting Tree View Verification via MCP...");
  const rootDir = process.cwd();

  const transport = new StdioClientTransport({
    command: "npx.cmd",
    args: ["playwright", "run-mcp-server"],
    cwd: rootDir,
  });

  const client = new Client(
    {
      name: "VerificationClient",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);
  console.log("Connected to Playwright MCP Server");

  try {
    // 1. Navigate
    console.log("Navigating to dashboard...");
    await client.callTool({
      name: "browser_navigate",
      arguments: { url: "http://localhost:5173" },
    });

    // 2. Wait for load
    console.log("Waiting for page load...");
    await client.callTool({
      name: "browser_run_code",
      arguments: {
        code: "await page.waitForLoadState('domcontentloaded');",
      },
    });

    // 3. Click Tree button
    console.log("Clicking 'Tree' button...");
    await client.callTool({
      name: "browser_run_code",
      arguments: {
        code: `
                const btn = page.getByRole('button', { name: 'Tree' });
                await btn.waitFor({ state: 'visible', timeout: 10000 });
                await btn.click();
            `,
      },
    });

    console.log("Taking debug screenshot after click...");
    await client.callTool({
      name: "browser_take_screenshot",
      arguments: { filename: "debug-tree-click.png" },
    });

    // 4. Verify Tree loads
    console.log("Waiting for tree structure...");
    const treeResult = await client.callTool({
      name: "browser_run_code",
      arguments: {
        code: `
                const tree = page.getByRole('tree');
                await tree.waitFor({ state: 'visible', timeout: 20000 });
                const nodes = await page.getByRole('treeitem').count();
                console.log('Tree nodes visible:', nodes);
                return nodes;
            `,
      },
    });
    console.log("Tree Verification Result:", treeResult);

    // 5. Expand a node
    console.log("Expanding first node...");
    await client.callTool({
      name: "browser_run_code",
      arguments: {
        code: `
                const firstNode = page.getByRole('treeitem').first();
                await firstNode.click(); // Select
                await page.keyboard.press('ArrowRight'); // Expand
                await page.waitForTimeout(500); // Wait for animation
            `,
      },
    });

    // 6. Screenshot
    console.log("Taking screenshot...");
    const screenshot = await client.callTool({
      name: "browser_take_screenshot",
      arguments: {
        filename: "verification-tree-view.png",
        fullPage: false,
      },
    });
    console.log("Screenshot saved.");
  } catch (error) {
    console.error("Verification Failed:", error);
    console.log("Taking error screenshot...");
    try {
      await client.callTool({
        name: "browser_take_screenshot",
        arguments: { filename: "error-state.png" },
      });
    } catch (e) {
      console.error("Could not take error screenshot");
    }
    process.exit(1);
  } finally {
    await client.close();
    process.exit(0);
  }
}

main().catch(console.error);
