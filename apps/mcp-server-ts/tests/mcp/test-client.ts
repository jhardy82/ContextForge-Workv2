/**
 * MCP Protocol Compliance Test - Client
 *
 * Purpose: Execute protocol tests against test server in all 3 modes
 * Evidence: CID-208 (Section 2.3 Phase 1 testing results)
 *
 * Test Execution:
 * 1. Mode "good" - Baseline validation (structuredContent only)
 * 2. Mode "bad" - Critical test (structured only - current implementation)
 * 3. Mode "both" - Edge case (both fields present)
 *
 * Observables:
 * - Does SDK throw/validate/reject at runtime?
 * - Which fields are present in client response?
 * - Are errors thrown or warnings logged?
 *
 * Decision Criteria:
 * - Branch A: SDK accepts 'structured' → document override
 * - Branch B: SDK rejects 'structured' → systemic fix needed
 * - Branch C: Unclear behavior → deep SDK investigation
 *
 * Run: npm run test:mcp-protocol
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

type TestMode = "good" | "bad" | "both";

interface TestResult {
  mode: TestMode;
  success: boolean;
  error?: any;
  toolsFound: number;
  hasOutputSchema: boolean;
  responseKeys: string[];
  structuredContentPresent: boolean;
  structuredPresent: boolean;
  dataAccessible: boolean;
  logs: string[];
}

async function runOnce(mode: TestMode): Promise<TestResult> {
  console.log(`\n${"=".repeat(60)}`);
  console.log(`MODE: ${mode.toUpperCase()}`);
  console.log(`${"=".repeat(60)}\n`);

  const result: TestResult = {
    mode,
    success: false,
    toolsFound: 0,
    hasOutputSchema: false,
    responseKeys: [],
    structuredContentPresent: false,
    structuredPresent: false,
    dataAccessible: false,
    logs: [],
  };

  // Spawn server process with test mode using tsx
  const serverPath = "tests/mcp/test-server.ts";
  console.error(`[DEBUG] serverPath variable value: "${serverPath}"`);
  console.error(`[DEBUG] serverPath type: ${typeof serverPath}`);
  console.error(`[DEBUG] serverPath length: ${serverPath.length}`);
  console.log(`[CLIENT] Spawning server: ${serverPath}`);

  const transport = new StdioClientTransport({
    command: "npx",
    args: ["tsx", serverPath],
    env: { ...process.env, MCP_MODE: mode },
  });
  const client = new Client(
    {
      name: "taskman-mcp-protocol-test-client",
      version: "0.0.1",
    },
    {
      capabilities: {},
    }
  );

  try {
    console.log("[CLIENT] Connecting to server...");
    await client.connect(transport);
    console.log("[CLIENT] ✅ Connected successfully");

    // Test 1: Tool Discovery
    console.log("\n[TEST 1] Tool Discovery (ListToolsRequest)");
    const toolsResp = await client.listTools();
    result.toolsFound = toolsResp.tools?.length ?? 0;

    console.log(`[CLIENT] Tools found: ${result.toolsFound}`);

    const testTool = (toolsResp.tools || []).find(
      (t) => t.name === "action_list_create"
    );

    if (!testTool) {
      throw new Error(
        "Test tool 'action_list_create' not found in ListTools response"
      );
    }

    result.hasOutputSchema = !!testTool.outputSchema;
    console.log(
      `[CLIENT] Test tool has outputSchema: ${result.hasOutputSchema}`
    );

    if (!result.hasOutputSchema) {
      throw new Error("Test tool missing outputSchema (required for test)");
    }

    // Test 2: Tool Invocation (CRITICAL - field validation)
    console.log(
      "\n[TEST 2] Tool Invocation (CallToolRequest) - CRITICAL FIELD VALIDATION"
    );
    console.log(`[CLIENT] Calling tool with mode: ${mode}`);

    const callResp = await client.callTool({
      name: "action_list_create",
      arguments: { name: `Test List (${mode} mode)` },
    });

    // Introspect response structure
    result.responseKeys = Object.keys(callResp || {});
    result.structuredContentPresent = "structuredContent" in (callResp || {});
    result.structuredPresent = "structured" in (callResp || {});

    console.log("\n[RESULT INSPECTION]");
    console.log(`Response keys: ${result.responseKeys.join(", ")}`);
    console.log(`Has 'structuredContent': ${result.structuredContentPresent}`);
    console.log(`Has 'structured': ${result.structuredPresent}`);

    // Check data accessibility
    const structuredContentData = (callResp as any)?.structuredContent;
    const structuredData = (callResp as any)?.structured;
    const contentData = (callResp as any)?.content?.[0]?.text;

    if (structuredContentData) {
      console.log(
        `✅ Data accessible via structuredContent:`,
        structuredContentData
      );
      result.dataAccessible = true;
    }

    if (structuredData) {
      console.log(
        `⚠️  Data accessible via structured (non-spec field):`,
        structuredData
      );
      result.dataAccessible = true;
    }

    if (contentData) {
      console.log(`📄 Data in content[0].text:`, contentData);
    }

    result.success = true;
    console.log("\n✅ Test completed successfully");
  } catch (error) {
    result.error = error;
    console.error("\n❌ Test failed with error:");
    console.error(error);
  } finally {
    console.log("\n[CLIENT] Cleaning up...");
    await client.close();
  }

  return result;
}

async function main() {
  console.log("MCP Protocol Compliance Test Suite");
  console.log("Evidence: CID-208 (Section 2.3 Phase 1)");
  console.log("SDK Version: @modelcontextprotocol/sdk@1.20.2\n");

  const results: TestResult[] = [];

  // Run all 3 test modes
  for (const mode of ["good", "bad", "both"] as TestMode[]) {
    const result = await runOnce(mode);
    results.push(result);

    // Brief delay between tests
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  // Generate evidence summary
  console.log("\n" + "=".repeat(60));
  console.log("EVIDENCE SUMMARY (CID-208)");
  console.log("=".repeat(60) + "\n");

  console.log(
    "| Mode | Success | structuredContent | structured | Data Accessible |"
  );
  console.log(
    "|------|---------|-------------------|------------|-----------------|"
  );

  for (const r of results) {
    const success = r.success ? "✅" : "❌";
    const scPresent = r.structuredContentPresent ? "✅" : "❌";
    const sPresent = r.structuredPresent ? "✅" : "❌";
    const accessible = r.dataAccessible ? "✅" : "❌";

    console.log(
      `| ${r.mode.padEnd(4)} | ${success.padEnd(7)} | ${scPresent.padEnd(
        17
      )} | ${sPresent.padEnd(10)} | ${accessible.padEnd(15)} |`
    );
  }

  // Decision analysis
  console.log("\n" + "=".repeat(60));
  console.log("DECISION ANALYSIS");
  console.log("=".repeat(60) + "\n");

  const badResult = results.find((r) => r.mode === "bad");

  if (!badResult) {
    console.log("❌ CRITICAL: 'bad' mode test did not execute");
    process.exit(1);
  }

  if (!badResult.success) {
    console.log("🔴 BRANCH B CONFIRMED: SDK REJECTS 'structured' field");
    console.log("\nEvidence:");
    console.log("- Test with 'structured' field FAILED");
    console.log("- SDK threw error or validation failed");
    console.log("\nRecommendation:");
    console.log(
      "- Apply SYSTEMIC FIX across all 3 features (action-lists, tasks, projects)"
    );
    console.log("- Change all 16 occurrences: structured → structuredContent");
    console.log("- Estimated time: 30-45 minutes + regression testing");
    console.log("\nNext Step: Create Section 2.3 Phase 2 fix implementation");
  } else if (
    badResult.structuredContentPresent &&
    !badResult.structuredPresent
  ) {
    console.log(
      "🟡 UNEXPECTED: SDK transformed 'structured' to 'structuredContent'"
    );
    console.log("\nEvidence:");
    console.log("- Test with 'structured' field succeeded");
    console.log("- Response contains 'structuredContent' but NOT 'structured'");
    console.log("- Possible SDK auto-correction or field mapping");
    console.log("\nRecommendation:");
    console.log(
      "- INVESTIGATE: Check SDK transport layer for field transformation"
    );
    console.log("- Consider this BRANCH C (unclear behavior)");
    console.log("\nNext Step: Deep SDK source code investigation");
  } else if (
    !badResult.structuredContentPresent &&
    badResult.structuredPresent
  ) {
    console.log("🟢 BRANCH A CONFIRMED: SDK ACCEPTS 'structured' field");
    console.log("\nEvidence:");
    console.log("- Test with 'structured' field succeeded");
    console.log("- Response contains 'structured' field with data accessible");
    console.log("- SDK does NOT enforce field name per documentation");
    console.log("\nRecommendation:");
    console.log("- DOCUMENT as working override in CID-208");
    console.log("- Add note explaining divergence from SDK spec");
    console.log("- Proceed directly to Section 2.4 (no fix needed)");
    console.log(
      "\nNext Step: Update evidence documents and continue to Section 2.4"
    );
  } else {
    console.log(
      "⚠️  BRANCH C: UNCLEAR BEHAVIOR (both fields present or neither)"
    );
    console.log("\nEvidence:");
    console.log(
      `- structuredContent present: ${badResult.structuredContentPresent}`
    );
    console.log(`- structured present: ${badResult.structuredPresent}`);
    console.log(`- Data accessible: ${badResult.dataAccessible}`);
    console.log("\nRecommendation:");
    console.log("- INVESTIGATE SDK validation logic in source code");
    console.log("- Review transport layer for field handling");
    console.log("- Re-run with DEBUG=mcp:* for verbose logging");
    console.log("\nNext Step: Section 2.3 Phase 2 - SDK source investigation");
  }

  console.log("\n" + "=".repeat(60));
  console.log(
    "Evidence captured in: evidence/Section-2-3-Protocol-Test-Results.md"
  );
  console.log("Correlation ID: CID-208");
  console.log("=".repeat(60) + "\n");
}

main().catch((err) => {
  console.error("Fatal test error:", err);
  process.exit(1);
});
