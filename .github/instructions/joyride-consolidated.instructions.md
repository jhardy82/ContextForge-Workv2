---
applyTo: "joyride*, clojurescript*, SCI*, vscode automation*, user script*, **/.joyride/**"
description: "Joyride VS Code automation - REPL-driven ClojureScript for user scripts and workspace automation"
version: "2.0-consolidated"
---

# Joyride VS Code Automation

**Authority**: Joyride Documentation | SCI ClojureScript | VS Code API

> Expert assistance for REPL-driven VS Code automation in user space.

---

## Essential Documentation

Use `fetch_webpage` for up-to-date guides:
- **Agent guide**: `https://raw.githubusercontent.com/BetterThanTomorrow/joyride/master/assets/llm-contexts/agent-joyride-eval.md`
- **User guide**: `https://raw.githubusercontent.com/BetterThanTomorrow/joyride/master/assets/llm-contexts/user-assistance.md`

---

## Core Philosophy: Interactive Programming

- **REPL First**: Evaluate features into existence; update files only when asked
- **Data-Oriented**: Functional code, args in → results out, minimal side effects
- **Step-by-Step**: Build solutions incrementally with the user
- **Verify First**: Always test API usage in REPL before updating files

### Code Style

- Use `(in-ns ...)` blocks to show REPL evaluations
- Prefer destructuring and maps for function arguments
- Use namespaced keywords (`:foo/something`, `:project/type`)
- Prefer flatness over depth in data modeling
- **Avoid** `println` / `js/console.log` - evaluate subexpressions instead

---

## Project Types

| Type | Location | Use For |
|------|----------|---------|
| **User Scripts** | `~/.config/joyride/` | Personal automation, global keybindings |
| **Workspace** | `.joyride/` | Project-specific, team-shareable, version-controlled |

---

## Essential APIs

### VS Code API
```clojure
(require '["vscode" :as vscode])

(vscode/window.showInformationMessage "Hello!")
(vscode/commands.executeCommand "workbench.action.files.save")
(vscode/window.showQuickPick #js ["Option 1" "Option 2"])
```

### Joyride Core
```clojure
(require '[joyride.core :as joyride])

joyride/*file*                    ; Current file path
(joyride/invoked-script)          ; Script being run (nil in REPL)
(joyride/extension-context)       ; VS Code extension context
joyride/slurp                     ; Async file read
joyride/load-file                 ; Async file load
```

### Async Handling
```clojure
(require '[promesa.core :as p])

(p/let [result (vscode/window.showInputBox #js {:prompt "Enter value:"})]
  (when result
    (vscode/window.showInformationMessage (str "You entered: " result))))
```

**`awaitResult` parameter**:
- `true`: Wait for async operations (user input, file operations)
- `false` (default): Fire-and-forget or synchronous operations

---

## Common Patterns

### Script Execution Guard
```clojure
(when (= (joyride/invoked-script) joyride/*file*)
  (main))
```

### Managing Disposables
```clojure
(let [disposable (vscode/workspace.onDidOpenTextDocument handler)]
  (.push (.-subscriptions (joyride/extension-context)) disposable))
```

### Extension API Access
```clojure
(when-let [ext (vscode/extensions.getExtension "ms-python.python")]
  (when (.-isActive ext)
    (let [api (.-exports ext)]
      (-> api .-environments .-known count))))
```

---

## Joyride Flares (WebViews)

```clojure
(require '[joyride.flare :as flare])

;; Panel flare
(flare/flare!+ {:html [:h1 "Hello World!"]
                :title "My Flare"
                :key "example"})

;; Sidebar flare (slots 1-5)
(flare/flare!+ {:html [:div [:h2 "Sidebar"]]
                :key :sidebar-1})

;; Management
(flare/close! key)
(flare/ls)
(flare/close-all!)
```

---

## Anti-Patterns

- Using `println` instead of evaluating subexpressions
- Updating files before verifying in REPL
- Missing script execution guards
- Not registering disposables with extension context
- Deep nesting instead of flat data structures

---

**Consolidated from**: `joyride-user-project.instructions.md`, `joyride-workspace-automation.instructions.md`

**Full Reference**: See archived files for complete API examples and flare documentation.
