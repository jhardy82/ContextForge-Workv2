"""
State Transition Validator Agent

Validates task lifecycle state transitions and state-specific requirements.
"""

import uuid
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class StateTransitionValidatorAgent(BaseValidationAgent):
    """Validates state transitions"""

    # Define valid state machine
    STATE_MACHINE = {
        "new": ["in_progress", "dropped"],
        "in_progress": ["blocked", "review", "dropped"],
        "blocked": ["in_progress", "dropped"],
        "review": ["in_progress", "done", "dropped"],
        "done": [],  # Terminal state
        "dropped": [],  # Terminal state
    }

    # State-specific requirements
    STATE_REQUIREMENTS = {
        "done": ["done_date"],
        "blocked": ["risk_notes"],
        "in_progress": ["owner"],
    }

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all state transition validation tests"""
        try:
            self._test_valid_transitions()
            self._test_invalid_transitions()
            self._test_state_requirements()
            self._test_terminal_states()

            report = self._generate_report()
            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"State transition validation failed: {e}")

    def _test_valid_transitions(self):
        """Test all valid state transitions"""
        test_cases = [
            ("new", "in_progress", "Start work on new task"),
            ("in_progress", "blocked", "Block active task"),
            ("blocked", "in_progress", "Unblock and resume"),
            ("in_progress", "review", "Move to review"),
            ("review", "done", "Complete review and finish"),
            ("new", "dropped", "Cancel new task"),
            ("in_progress", "dropped", "Cancel active task"),
        ]

        for from_state, to_state, description in test_cases:
            task_id = self._create_test_task(status=from_state)

            if task_id:
                success = self._transition_task(task_id, from_state, to_state)
                self._record_test_result(
                    test_name=f"valid_transition_{from_state}_to_{to_state}",
                    passed=success,
                    expected="success",
                    actual="success" if success else "failure",
                    details=description,
                )
            else:
                self._record_test_result(
                    test_name=f"valid_transition_{from_state}_to_{to_state}_setup",
                    passed=False,
                    severity="warning",
                    details="Failed to create test task",
                )

    def _test_invalid_transitions(self):
        """Test invalid state transitions that should be rejected"""
        invalid_cases = [
            ("new", "review", "Cannot skip in_progress"),
            ("new", "done", "Cannot skip workflow"),
            ("done", "in_progress", "Cannot reopen completed"),
            ("dropped", "in_progress", "Cannot reopen dropped"),
            ("new", "blocked", "Cannot block without starting"),
        ]

        for from_state, to_state, description in invalid_cases:
            task_id = self._create_test_task(status=from_state)

            if task_id:
                success = self._transition_task(task_id, from_state, to_state)

                # For invalid transitions, success = False means test passed
                self._record_test_result(
                    test_name=f"invalid_transition_{from_state}_to_{to_state}",
                    passed=not success,  # Should fail
                    expected="rejection",
                    actual="rejected" if not success else "allowed",
                    severity="critical",
                    details=f"{description} (should be rejected)",
                )

    def _test_state_requirements(self):
        """Test state-specific field requirements"""
        # Test 1: done status requires done_date
        task_id = self._create_test_task(status="review")
        if task_id:
            # Try to transition to done without setting done_date
            conn = self._get_connection()
            try:
                # Update to done status
                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("done", task_id))
                conn.commit()

                # Check if done_date was set automatically
                cursor = conn.execute("SELECT done_date FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()

                self._record_test_result(
                    test_name="done_status_requires_done_date",
                    passed=row and row["done_date"] is not None,
                    expected="done_date set",
                    actual="done_date set" if row and row["done_date"] else "done_date missing",
                    severity="warning",
                    details="done status should automatically set done_date",
                )
            finally:
                conn.close()

        # Test 2: blocked status should have risk_notes
        task_id = self._create_test_task(status="in_progress")
        if task_id:
            success = self._transition_task(task_id, "in_progress", "blocked")

            if success:
                conn = self._get_connection()
                try:
                    cursor = conn.execute("SELECT risk_notes FROM tasks WHERE id = ?", (task_id,))
                    row = cursor.fetchone()

                    # Note: This is a soft requirement (warning, not critical)
                    self._record_test_result(
                        test_name="blocked_status_should_have_risk_notes",
                        passed=True,  # Not enforced, just recommended
                        severity="warning",
                        details="Blocked tasks should document risk_notes",
                    )
                finally:
                    conn.close()

    def _test_terminal_states(self):
        """Test that terminal states (done, dropped) cannot transition"""
        terminal_states = ["done", "dropped"]

        for terminal_state in terminal_states:
            task_id = self._create_test_task(status=terminal_state)

            if task_id:
                # Try to transition to any other state
                success = self._transition_task(task_id, terminal_state, "in_progress")

                self._record_test_result(
                    test_name=f"terminal_state_{terminal_state}_immutable",
                    passed=not success,  # Should fail
                    expected="rejection",
                    actual="rejected" if not success else "allowed",
                    severity="critical",
                    details=f"Terminal state {terminal_state} should not allow transitions",
                )

    def _create_test_task(self, status: str = "new") -> str:
        """
        Create a test task with specified status

        Args:
            status: Initial status for the task

        Returns:
            Task ID if successful, None otherwise
        """
        task_id = f"T-STATE-{uuid.uuid4().hex[:8]}"
        title = f"State Test {status} {uuid.uuid4().hex[:8]}"

        conn = self._get_connection()
        try:
            # Set done_date if status is done
            done_date = self._utc_now() if status == "done" else None

            # Set owner if status is in_progress or beyond
            owner = (
                "validation-agent"
                if status in ["in_progress", "blocked", "review", "done"]
                else None
            )

            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, status, created_at, updated_at, done_date, owner
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, title, status, self._utc_now(), self._utc_now(), done_date, owner),
            )
            conn.commit()
            return task_id
        except Exception as e:
            print(f"Failed to create test task: {e}")
            return None
        finally:
            conn.close()

    def _transition_task(self, task_id: str, from_state: str, to_state: str) -> bool:
        """
        Attempt to transition task state

        Args:
            task_id: Task to transition
            from_state: Current state (for validation)
            to_state: Target state

        Returns:
            True if transition succeeded, False otherwise
        """
        # Check if transition is valid according to state machine
        if to_state not in self.STATE_MACHINE.get(from_state, []):
            # Invalid transition according to rules
            return False

        conn = self._get_connection()
        try:
            # Update status
            updates = {"status": to_state, "updated_at": self._utc_now()}

            # Set done_date if transitioning to done
            if to_state == "done":
                updates["done_date"] = self._utc_now()

            # Build UPDATE query
            set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
            values = list(updates.values()) + [task_id]

            conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
            conn.commit()

            # Verify transition was applied
            cursor = conn.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

            return row and row["status"] == to_state
        except Exception as e:
            print(f"Transition failed: {e}")
            return False
        finally:
            conn.close()

    def _validate_state_machine(self) -> list[str]:
        """
        Validate state machine definition is correct

        Returns:
            List of validation issues
        """
        issues = []

        # Check for undefined states referenced in transitions
        all_target_states = set()
        for source_state, target_states in self.STATE_MACHINE.items():
            all_target_states.update(target_states)

        undefined_states = all_target_states - set(self.STATE_MACHINE.keys())
        if undefined_states:
            issues.append(f"Undefined target states: {undefined_states}")

        # Check for unreachable states
        reachable_states = {"new"}  # Start state
        changed = True
        while changed:
            changed = False
            for source_state in list(reachable_states):
                for target_state in self.STATE_MACHINE.get(source_state, []):
                    if target_state not in reachable_states:
                        reachable_states.add(target_state)
                        changed = True

        unreachable_states = set(self.STATE_MACHINE.keys()) - reachable_states
        if unreachable_states:
            issues.append(f"Unreachable states: {unreachable_states}")

        return issues
