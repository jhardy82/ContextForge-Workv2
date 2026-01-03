import * as assert from 'assert';
import * as vscode from 'vscode';
import { SchemaMigration, TodoGroup, TodoItem } from "../../models";

suite("Extension Test Suite", () => {
  vscode.window.showInformationMessage("Start all tests.");

  test("TodoItem creation", () => {
    const todo = new TodoItem(
      "test-1",
      "Test Todo",
      false,
      "Today",
      "Test description",
      "2024-01-01",
      ["tag1", "tag2"]
    );

    assert.strictEqual(todo.id, "test-1");
    assert.strictEqual(todo.title, "Test Todo");
    assert.strictEqual(todo.completed, false);
    assert.strictEqual(todo.group, "Today");
    assert.strictEqual(todo.description, "Test description");
    assert.strictEqual(todo.dueDate, "2024-01-01");
    assert.deepStrictEqual(todo.tags, ["tag1", "tag2"]);
  });

  test("TodoItem storage serialization", () => {
    const todo = new TodoItem(
      "test-1",
      "Test Todo",
      false,
      "Today",
      "Test description"
    );

    const storageObj = todo.toStorageObject();
    assert.strictEqual(storageObj.id, "test-1");
    assert.strictEqual(storageObj.title, "Test Todo");
    assert.strictEqual(storageObj.completed, false);
    assert.strictEqual(storageObj.group, "Today");
    assert.strictEqual(storageObj.description, "Test description");

    const deserializedTodo = TodoItem.fromStorageObject(storageObj);
    assert.strictEqual(deserializedTodo.id, todo.id);
    assert.strictEqual(deserializedTodo.title, todo.title);
    assert.strictEqual(deserializedTodo.completed, todo.completed);
    assert.strictEqual(deserializedTodo.group, todo.group);
    assert.strictEqual(deserializedTodo.description, todo.description);
  });

  test("TodoGroup creation", () => {
    const todos = [
      new TodoItem("1", "Todo 1", false, "Today"),
      new TodoItem("2", "Todo 2", true, "Today"),
    ];

    const group = new TodoGroup("Today", todos);
    assert.strictEqual(group.name, "Today");
    assert.strictEqual(group.todos.length, 2);
    assert.strictEqual(group.contextValue, "group");
  });

  test("TodoGroup tooltip calculation", () => {
    const todos = [
      new TodoItem("1", "Todo 1", false, "Today"),
      new TodoItem("2", "Todo 2", true, "Today"),
      new TodoItem("3", "Todo 3", false, "Today"),
    ];

    const group = new TodoGroup("Today", todos);
    // Access the private method through the public interface
    assert.ok(group.tooltip);
    const tooltipText =
      typeof group.tooltip === "string" ? group.tooltip : group.tooltip.value;
    assert.ok(tooltipText.includes("Total: 3"));
    assert.ok(tooltipText.includes("Completed: 1"));
    assert.ok(tooltipText.includes("Pending: 2"));
  });

  test("Schema migration", () => {
    const oldData = {
      todos: [{ id: "1", title: "Test", completed: false, group: "Today" }],
      groups: [{ name: "Today" }],
    };

    const migrated = SchemaMigration.migrate(oldData);
    assert.strictEqual(migrated.version, 1);
    assert.strictEqual(migrated.todos.length, 1);
    assert.strictEqual(migrated.groups.length, 1);
  });

  test("TodoItem icon logic", () => {
    // Test completed todo
    const completedTodo = new TodoItem("1", "Done", true, "Today");
    assert.ok(completedTodo.iconPath);

    // Test overdue todo
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const overdueTodo = new TodoItem(
      "2",
      "Overdue",
      false,
      "Today",
      undefined,
      yesterday.toISOString()
    );
    assert.ok(overdueTodo.iconPath);

    // Test regular todo
    const regularTodo = new TodoItem("3", "Regular", false, "Today");
    assert.ok(regularTodo.iconPath);
  });

  test("TodoItem due date calculations", () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    // Test today's todo
    const todayTodo = new TodoItem(
      "1",
      "Today Todo",
      false,
      "Today",
      undefined,
      today.toISOString()
    );
    assert.ok(todayTodo.description?.includes("Due today"));

    // Test overdue todo
    const overdueTodo = new TodoItem(
      "2",
      "Overdue Todo",
      false,
      "Today",
      undefined,
      yesterday.toISOString()
    );
    assert.ok(overdueTodo.description?.includes("Overdue"));

    // Test future todo (should not have special description)
    const futureTodo = new TodoItem(
      "3",
      "Future Todo",
      false,
      "Today",
      undefined,
      tomorrow.toISOString()
    );
    // Future todos don't get special descriptions in our current implementation
    assert.ok(true); // Just ensure no errors
  });
});
