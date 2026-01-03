---
applyTo: "**/*.py"
version: "1.0"
---
# Python Research Guide

## 1. Purpose

* Use these instructions when writing, maintaining, testing, or refactoring Python code in this repository.
* Goal: maximize correctness, security, and maintainability using modern Python practices and high-quality research.

## 2. Source hierarchy and conflict handling

When you need information beyond the current workspace, follow this order:

1. **Context7 MCP (Tier 1)**

   * Query Context7 first for Python-related knowledge, prior research, and internal patterns.
   * Treat Context7 as the primary source when it agrees with current official documentation.
2. **Microsoft Learn and official vendor docs (Tier 2)**

   * Use for Python on Azure, DevOps, data services, and related Microsoft integrations.
   * Prefer pages under learn.microsoft.com and official vendor GitHub repositories.
   * When Tier 1 and Tier 2 disagree, prefer Tier 2 and clearly note the conflict.
3. **Validated web sources (Tier 3)**

   * Use only after Tiers 1 and 2 are insufficient.
   * Prefer: python.org docs, PyPI project pages, official library docs, and reputable technical references.
   * Avoid relying on single, unverified blog posts.

**Staleness and recency**

* When official docs appear out of date compared to release notes, changelogs, or migration guides, note the discrepancy.
* If multiple recent, reputable sources contradict older documentation, explain the conflict and lower your confidence score.

## 3. When to research vs local reasoning

* **Do NOT perform external research when:**

  * The answer is clearly derivable from code already loaded in context.
  * The user explicitly asks for local reasoning only.
  * The task is limited to formatting, renaming, or small mechanical edits.
* **Perform external research when:**

  * Introducing or upgrading libraries or frameworks.
  * Designing new APIs, modules, or services.
  * Making security, performance, or architecture impacting changes.
  * Working with unfamiliar domains, protocols, or integrations.

## 4. Research intensity levels

Use research intensity levels to decide how deep to go.

### 4.1 Intensity definitions

**Low intensity (quick check)**

* Use when confirming syntax, minor behavior details, or small configuration questions.
* One or two high-quality sources.
* Output: short answer and a 1 to 3 bullet source list.

**Medium intensity (design decision)**

* Use for choosing between approaches, patterns, or common libraries.
* Three to five sources; compare trade-offs and ecosystem health.
* Output: summary of options, a brief pros and cons table, and a clear recommendation.

**High intensity (architecture or new stack)**

* Use for new subsystems, major refactors, or new core dependencies.
* Broad search across tiers, plus any relevant internal docs.
* Output: structured mini-report with headings: Problem, Options, Analysis, Risks, Recommendation, Follow up.

### 4.2 Task type to intensity mapping

Use this table to choose the default intensity.

| Task type                                                             | Default intensity |
| --------------------------------------------------------------------- | ----------------- |
| Simple syntax or standard library question                            | Low               |
| Clarifying behavior of an existing library already used in the repo   | Low               |
| Writing small utility functions or helpers with no new dependencies   | Low               |
| Choosing between two or more libraries for a new feature              | Medium            |
| Designing or refactoring a public module or package API               | Medium            |
| Designing error handling, logging, or configuration strategy          | Medium            |
| Introducing a new core dependency (framework, ORM, messaging client)  | High              |
| Upgrading a core dependency across major versions                     | High              |
| Making changes that affect security, authentication, or authorization | High              |
| Changes that will significantly alter performance characteristics     | High              |

Adjust intensity upward if the change affects many modules, critical paths, or external contracts.

## 5. Research workflow

When external research is needed:

1. Define the question and scope in one to three bullet points.
2. Query Context7 for existing knowledge, prior experiments, or patterns.
3. If needed, query Microsoft Learn or official vendor docs for platform details.
4. If still unresolved, perform web searches and read multiple independent sources.
5. Cross-check findings across tiers; resolve or explicitly note conflicts.
6. Produce a concise summary and recommendation appropriate to the intensity level.
7. When results are generally reusable, add a short summary back into the internal knowledge base via Context7.

## 6. Library and plugin research

When using or modifying external Python packages:

* Identify the canonical package name, latest stable version, and minimum supported version in this project.
* Read the official documentation or README for:

  * Primary use cases and core APIs.
  * Supported Python versions.
  * Compatibility with frameworks in this repository (for example: FastAPI, Django, Flask, Typer).
* Check:

  * Maintenance status (recent releases, open issues, responsiveness).
  * License compatibility with this project.
  * Security advisories or deprecation notices when relevant.
* Prefer widely used, actively maintained libraries over niche or abandoned ones, unless there is a strong reason.
* Propose migration paths when you discover that an existing dependency is deprecated, unmaintained, or replaced.

## 7. Modern Python practices

When proposing Python code or changes:

* Target the latest stable Python 3.x that matches the project configuration without assuming upgrades.
* Prefer:

  * Type hints and static type checking compatibility.
  * Clean module boundaries and clear public APIs.
  * pytest-style tests with fixtures and parametrization where applicable.
  * Readable, well-structured functions and classes over clever one-liners.
  * Standard library features when they adequately solve the problem.
* Avoid:

  * Introducing heavy dependencies for trivial tasks.
  * Using outdated patterns that conflict with current best practices.

## 8. Testing and quality expectations

* Whenever you add or change behavior, consider appropriate automated tests:

  * Unit tests for core logic.
  * Integration tests for I/O, networking, or database interactions.
  * Property-based tests where they provide value.
* Ensure examples and snippets you produce are:

  * Runnable in principle.
  * Consistent with the project’s existing test layout and tools.
* When uncertain about test style, briefly inspect existing tests and follow their conventions.

## 9. Confidence scoring and behavior

For any non-trivial research-backed answer, include a confidence score and use it to shape your response.

### 9.1 Scoring scale

* Use a numeric value between 0.0 and 1.0, for example: `Confidence: 0.92`.
* Thresholds:

  * 0.90 or higher: high confidence.
  * 0.60 to 0.89: moderate confidence; mention key uncertainties or alternatives.
  * Below 0.60: low confidence; clearly label the answer as tentative and suggest validation steps.

### 9.2 Scoring heuristic

When computing the confidence score:

* Start from a baseline of 0.6.
* Add 0.15 if Context7 and at least one official doc (Tier 2) agree.
* Add 0.10 if at least two independent reputable Tier 3 sources agree with Tiers 1 and 2.
* Subtract 0.15 if there is an unresolved conflict between tiers.
* Subtract 0.10 if documentation is clearly out of date or ambiguous.
* Clamp the final score to the range [0.0, 1.0].

This heuristic is approximate. Use judgment when the situation does not fit these increments, but always keep the thresholds in mind.

### 9.3 Behavior by confidence level

* For **high confidence** answers (0.90 or higher):

  * Present a single, clear recommendation.
  * Briefly list the main supporting sources.
* For **moderate confidence** answers (0.60 to 0.89):

  * Highlight key uncertainties and viable alternatives.
  * Suggest simple validation steps that a developer can run.
* For **low confidence** answers (below 0.60):

  * Label the answer as tentative.
  * Clearly state what is unknown or disputed.
  * Provide specific next research or validation steps.

### 9.4 Placement and `<UNVERIFIED>`

* Place the confidence line near the end of your response on its own line, for example:

  * `Confidence: 0.84`
* When you cannot locate trustworthy sources for a critical claim:

  * Mark that claim with `<UNVERIFIED>` and explain what information is missing.
  * Lower the overall confidence score accordingly.

## 10. Token efficiency

* Prefer concise summaries over long quotations.
* Link to or reference external docs instead of copying large excerpts.
* Avoid repeating the same explanation in multiple places within a single response.
* When multiple questions overlap, factor shared explanations into a single, clear section.

## 11. Maintenance

* Treat these instructions as the default Python research policy for this repository.
* If you discover that a recurring pattern or decision is not covered, propose an update to this file in your explanation.
* Keep changes minimal and focused to preserve clarity and token efficiency.
