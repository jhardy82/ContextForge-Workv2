"""Integration tests for State Store API endpoints.

Tests E2E functionality of Conversations, Plans, and Checklists.
"""

from fastapi import status


class TestConversationEndpoints:
    """Test conversation session API endpoints."""

    async def test_create_conversation_success(self, client):
        """Test successful conversation creation."""
        conv_data = {
            "id": "CONV-TEST-001",
            "title": "Test Conversation",
            "agent_type": "claude",
            "worktree": "test-worktree",
            "project_id": "P-001",
        }

        response = await client.post("/api/v1/conversations", json=conv_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "CONV-TEST-001"
        assert data["title"] == "Test Conversation"
        assert data["status"] == "active"
        assert data["turn_count"] == 0
        assert data["token_estimate"] == 0

    async def test_get_conversation_success(self, client):
        """Test getting conversation by ID."""
        # Create conversation first
        conv_data = {
            "id": "CONV-GET-001",
            "title": "Get Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Get conversation
        response = await client.get("/api/v1/conversations/CONV-GET-001")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "CONV-GET-001"

    async def test_get_conversation_not_found(self, client):
        """Test getting non-existent conversation returns 404."""
        response = await client.get("/api/v1/conversations/CONV-NONEXISTENT")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_conversation_success(self, client):
        """Test updating conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-UPDATE-001",
            "title": "Original Title",
            "agent_type": "claude",
        }
        create_response = await client.post("/api/v1/conversations", json=conv_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Update conversation
        update_data = {"title": "Updated Title", "summary": "New summary"}
        response = await client.patch(
            "/api/v1/conversations/CONV-UPDATE-001", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["summary"] == "New summary"

    async def test_delete_conversation_success(self, client):
        """Test deleting conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-DELETE-001",
            "title": "Delete Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Delete conversation
        response = await client.delete("/api/v1/conversations/CONV-DELETE-001")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = await client.get("/api/v1/conversations/CONV-DELETE-001")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_conversations(self, client):
        """Test listing conversations with pagination."""
        # Create multiple conversations
        for i in range(5):
            conv_data = {
                "id": f"CONV-LIST-{i:03d}",
                "title": f"Conversation {i}",
                "agent_type": "claude",
            }
            await client.post("/api/v1/conversations", json=conv_data)

        # List conversations
        response = await client.get("/api/v1/conversations?limit=10&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    async def test_create_conversation_conflict(self, client):
        """Test duplicate conversation ID returns 409."""
        conv_data = {
            "id": "CONV-CONFLICT-001",
            "title": "Conflict Test",
            "agent_type": "claude",
        }

        # Create first conversation
        first_response = await client.post("/api/v1/conversations", json=conv_data)
        assert first_response.status_code == status.HTTP_201_CREATED

        # Attempt to create duplicate
        duplicate_response = await client.post("/api/v1/conversations", json=conv_data)

        assert duplicate_response.status_code == status.HTTP_409_CONFLICT

    async def test_create_conversation_validation_error(self, client):
        """Test validation error returns 422."""
        conv_data = {
            "id": "CONV-INVALID",
            "title": "",  # Empty title should fail validation
            "agent_type": "claude",
        }

        response = await client.post("/api/v1/conversations", json=conv_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_complete_conversation(self, client):
        """Test completing a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-COMPLETE-001",
            "title": "Complete Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Complete conversation
        response = await client.post(
            "/api/v1/conversations/CONV-COMPLETE-001/complete?summary=Final%20summary"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_pause_and_resume_conversation(self, client):
        """Test pausing and resuming a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-PAUSE-001",
            "title": "Pause Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Pause conversation
        pause_response = await client.post(
            "/api/v1/conversations/CONV-PAUSE-001/pause"
        )
        assert pause_response.status_code == status.HTTP_200_OK
        assert pause_response.json()["status"] == "paused"

        # Resume conversation
        resume_response = await client.post(
            "/api/v1/conversations/CONV-PAUSE-001/resume"
        )
        assert resume_response.status_code == status.HTTP_200_OK
        assert resume_response.json()["status"] == "active"

    async def test_archive_conversation(self, client):
        """Test archiving a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-ARCHIVE-001",
            "title": "Archive Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Archive conversation
        response = await client.post(
            "/api/v1/conversations/CONV-ARCHIVE-001/archive"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "archived"

    async def test_add_turn_to_conversation(self, client):
        """Test adding a turn to a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-TURN-001",
            "title": "Turn Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Add turn
        turn_data = {
            "id": "TURN-001",
            "conversation_id": "CONV-TURN-001",
            "sequence": 1,
            "role": "user",
            "content": "Hello, world!",
            "token_count": 10,
        }
        response = await client.post(
            "/api/v1/conversations/CONV-TURN-001/turns", json=turn_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "TURN-001"
        assert data["role"] == "user"
        assert data["content"] == "Hello, world!"

    async def test_get_turns_for_conversation(self, client):
        """Test getting turns for a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-TURNS-001",
            "title": "Turns Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Add multiple turns
        for i in range(3):
            turn_data = {
                "id": f"TURN-LIST-{i:03d}",
                "conversation_id": "CONV-TURNS-001",
                "sequence": i + 1,
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}",
                "token_count": 10,
            }
            await client.post(
                "/api/v1/conversations/CONV-TURNS-001/turns", json=turn_data
            )

        # Get turns
        response = await client.get("/api/v1/conversations/CONV-TURNS-001/turns")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    async def test_link_plan_to_conversation(self, client):
        """Test linking a plan to a conversation."""
        # Create conversation
        conv_data = {
            "id": "CONV-LINK-001",
            "title": "Link Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Link plan
        response = await client.post(
            "/api/v1/conversations/CONV-LINK-001/link-plan?plan_id=PLAN-001"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "PLAN-001" in data["plan_ids"]

    async def test_search_conversations(self, client):
        """Test searching conversations with filters."""
        # Create conversations with different properties
        conv1 = {
            "id": "CONV-SEARCH-001",
            "title": "Search Test 1",
            "agent_type": "claude",
            "project_id": "P-SEARCH",
        }
        conv2 = {
            "id": "CONV-SEARCH-002",
            "title": "Search Test 2",
            "agent_type": "gpt",
            "project_id": "P-OTHER",
        }
        await client.post("/api/v1/conversations", json=conv1)
        await client.post("/api/v1/conversations", json=conv2)

        # Search by project
        response = await client.get(
            "/api/v1/conversations/search?project_id=P-SEARCH"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_active_conversations(self, client):
        """Test getting active conversations."""
        # Create active conversation
        conv_data = {
            "id": "CONV-ACTIVE-001",
            "title": "Active Test",
            "agent_type": "claude",
        }
        await client.post("/api/v1/conversations", json=conv_data)

        # Get active conversations
        response = await client.get("/api/v1/conversations/active")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_conversation_stats(self, client):
        """Test getting conversation statistics."""
        response = await client.get("/api/v1/conversations/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)


class TestPlanEndpoints:
    """Test plan API endpoints."""

    async def test_create_plan_success(self, client):
        """Test successful plan creation."""
        plan_data = {
            "id": "PLAN-TEST-001",
            "title": "Test Plan",
            "description": "Test description",
            "steps": [
                {"id": "STEP-001", "order": 1, "title": "Step 1"},
                {"id": "STEP-002", "order": 2, "title": "Step 2"},
            ],
        }

        response = await client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "PLAN-TEST-001"
        assert data["title"] == "Test Plan"
        assert data["status"] == "draft"
        assert len(data["steps"]) == 2

    async def test_get_plan_success(self, client):
        """Test getting plan by ID."""
        # Create plan
        plan_data = {
            "id": "PLAN-GET-001",
            "title": "Get Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Get plan
        response = await client.get("/api/v1/plans/PLAN-GET-001")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "PLAN-GET-001"

    async def test_get_plan_not_found(self, client):
        """Test getting non-existent plan returns 404."""
        response = await client.get("/api/v1/plans/PLAN-NONEXISTENT")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_plan_success(self, client):
        """Test updating plan."""
        # Create plan
        plan_data = {
            "id": "PLAN-UPDATE-001",
            "title": "Original Title",
        }
        create_response = await client.post("/api/v1/plans", json=plan_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Update plan
        update_data = {"title": "Updated Title", "description": "New description"}
        response = await client.patch("/api/v1/plans/PLAN-UPDATE-001", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"

    async def test_delete_plan_success(self, client):
        """Test deleting plan."""
        # Create plan
        plan_data = {
            "id": "PLAN-DELETE-001",
            "title": "Delete Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Delete plan
        response = await client.delete("/api/v1/plans/PLAN-DELETE-001")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = await client.get("/api/v1/plans/PLAN-DELETE-001")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_plans(self, client):
        """Test listing plans with pagination."""
        # Create multiple plans
        for i in range(5):
            plan_data = {
                "id": f"PLAN-LIST-{i:03d}",
                "title": f"Plan {i}",
            }
            await client.post("/api/v1/plans", json=plan_data)

        # List plans
        response = await client.get("/api/v1/plans?limit=10&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    async def test_create_plan_conflict(self, client):
        """Test duplicate plan ID returns 409."""
        plan_data = {
            "id": "PLAN-CONFLICT-001",
            "title": "Conflict Test",
        }

        # Create first plan
        first_response = await client.post("/api/v1/plans", json=plan_data)
        assert first_response.status_code == status.HTTP_201_CREATED

        # Attempt to create duplicate
        duplicate_response = await client.post("/api/v1/plans", json=plan_data)

        assert duplicate_response.status_code == status.HTTP_409_CONFLICT

    async def test_create_plan_validation_error(self, client):
        """Test validation error returns 422."""
        plan_data = {
            "id": "PLAN-INVALID",
            "title": "",  # Empty title should fail validation
        }

        response = await client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_approve_plan(self, client):
        """Test approving a draft plan."""
        # Create plan
        plan_data = {
            "id": "PLAN-APPROVE-001",
            "title": "Approve Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Approve plan
        response = await client.post("/api/v1/plans/PLAN-APPROVE-001/approve")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "approved"
        assert data["approved_at"] is not None

    async def test_start_plan(self, client):
        """Test starting an approved plan."""
        # Create and approve plan
        plan_data = {
            "id": "PLAN-START-001",
            "title": "Start Test",
            "steps": [{"id": "STEP-001", "order": 1, "title": "Step 1"}],
        }
        await client.post("/api/v1/plans", json=plan_data)
        await client.post("/api/v1/plans/PLAN-START-001/approve")

        # Start plan
        response = await client.post("/api/v1/plans/PLAN-START-001/start")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"

    async def test_abandon_plan(self, client):
        """Test abandoning a plan."""
        # Create plan
        plan_data = {
            "id": "PLAN-ABANDON-001",
            "title": "Abandon Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Abandon plan
        response = await client.post(
            "/api/v1/plans/PLAN-ABANDON-001/abandon?reason=No%20longer%20needed"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "abandoned"

    async def test_complete_step(self, client):
        """Test completing a plan step."""
        # Create, approve, and start plan
        plan_data = {
            "id": "PLAN-STEP-001",
            "title": "Step Test",
            "steps": [{"id": "STEP-001", "order": 1, "title": "Step 1"}],
        }
        await client.post("/api/v1/plans", json=plan_data)
        await client.post("/api/v1/plans/PLAN-STEP-001/approve")
        await client.post("/api/v1/plans/PLAN-STEP-001/start")

        # Complete step
        response = await client.post(
            "/api/v1/plans/PLAN-STEP-001/steps/STEP-001/complete"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        step = next(s for s in data["steps"] if s["id"] == "STEP-001")
        assert step["status"] == "completed"

    async def test_skip_step(self, client):
        """Test skipping a plan step."""
        # Create, approve, and start plan
        plan_data = {
            "id": "PLAN-SKIP-001",
            "title": "Skip Test",
            "steps": [{"id": "STEP-001", "order": 1, "title": "Step 1"}],
        }
        await client.post("/api/v1/plans", json=plan_data)
        await client.post("/api/v1/plans/PLAN-SKIP-001/approve")
        await client.post("/api/v1/plans/PLAN-SKIP-001/start")

        # Skip step
        response = await client.post(
            "/api/v1/plans/PLAN-SKIP-001/steps/STEP-001/skip?reason=Not%20applicable"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        step = next(s for s in data["steps"] if s["id"] == "STEP-001")
        assert step["status"] == "skipped"

    async def test_add_step_to_plan(self, client):
        """Test adding a step to a plan."""
        # Create plan
        plan_data = {
            "id": "PLAN-ADDSTEP-001",
            "title": "Add Step Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Add step
        step_data = {
            "id": "STEP-NEW-001",
            "order": 1,
            "title": "New Step",
        }
        response = await client.post(
            "/api/v1/plans/PLAN-ADDSTEP-001/steps", json=step_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["steps"]) == 1
        assert data["steps"][0]["id"] == "STEP-NEW-001"

    async def test_search_plans(self, client):
        """Test searching plans with filters."""
        # Create plans with different properties
        plan1 = {
            "id": "PLAN-SEARCH-001",
            "title": "Search Test 1",
            "project_id": "P-SEARCH",
        }
        plan2 = {
            "id": "PLAN-SEARCH-002",
            "title": "Search Test 2",
            "project_id": "P-OTHER",
        }
        await client.post("/api/v1/plans", json=plan1)
        await client.post("/api/v1/plans", json=plan2)

        # Search by project
        response = await client.get("/api/v1/plans/search?project_id=P-SEARCH")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_draft_plans(self, client):
        """Test getting draft plans."""
        # Create draft plan
        plan_data = {
            "id": "PLAN-DRAFT-001",
            "title": "Draft Test",
        }
        await client.post("/api/v1/plans", json=plan_data)

        # Get draft plans
        response = await client.get("/api/v1/plans/drafts")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_in_progress_plans(self, client):
        """Test getting in-progress plans."""
        response = await client.get("/api/v1/plans/in-progress")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_stalled_plans(self, client):
        """Test getting stalled plans."""
        response = await client.get("/api/v1/plans/stalled?days_inactive=3")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_plan_stats(self, client):
        """Test getting plan statistics."""
        response = await client.get("/api/v1/plans/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)


class TestChecklistEndpoints:
    """Test checklist API endpoints."""

    async def test_create_checklist_success(self, client):
        """Test successful checklist creation."""
        checklist_data = {
            "id": "CL-TEST-001",
            "title": "Test Checklist",
            "description": "Test description",
            "items": [
                {"id": "CLI-001", "order": 1, "title": "Item 1"},
                {"id": "CLI-002", "order": 2, "title": "Item 2"},
            ],
        }

        response = await client.post("/api/v1/checklists", json=checklist_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "CL-TEST-001"
        assert data["title"] == "Test Checklist"
        assert data["status"] == "active"
        assert len(data["items"]) == 2

    async def test_get_checklist_success(self, client):
        """Test getting checklist by ID."""
        # Create checklist
        checklist_data = {
            "id": "CL-GET-001",
            "title": "Get Test",
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Get checklist
        response = await client.get("/api/v1/checklists/CL-GET-001")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "CL-GET-001"

    async def test_get_checklist_not_found(self, client):
        """Test getting non-existent checklist returns 404."""
        response = await client.get("/api/v1/checklists/CL-NONEXISTENT")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_checklist_success(self, client):
        """Test updating checklist."""
        # Create checklist
        checklist_data = {
            "id": "CL-UPDATE-001",
            "title": "Original Title",
        }
        create_response = await client.post("/api/v1/checklists", json=checklist_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Update checklist
        update_data = {"title": "Updated Title", "description": "New description"}
        response = await client.patch(
            "/api/v1/checklists/CL-UPDATE-001", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"

    async def test_delete_checklist_success(self, client):
        """Test deleting checklist."""
        # Create checklist
        checklist_data = {
            "id": "CL-DELETE-001",
            "title": "Delete Test",
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Delete checklist
        response = await client.delete("/api/v1/checklists/CL-DELETE-001")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = await client.get("/api/v1/checklists/CL-DELETE-001")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_checklists(self, client):
        """Test listing checklists with pagination."""
        # Create multiple checklists
        for i in range(5):
            checklist_data = {
                "id": f"CL-LIST-{i:03d}",
                "title": f"Checklist {i}",
            }
            await client.post("/api/v1/checklists", json=checklist_data)

        # List checklists
        response = await client.get("/api/v1/checklists?limit=10&offset=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    async def test_create_checklist_conflict(self, client):
        """Test duplicate checklist ID returns 409."""
        checklist_data = {
            "id": "CL-CONFLICT-001",
            "title": "Conflict Test",
        }

        # Create first checklist
        first_response = await client.post("/api/v1/checklists", json=checklist_data)
        assert first_response.status_code == status.HTTP_201_CREATED

        # Attempt to create duplicate
        duplicate_response = await client.post("/api/v1/checklists", json=checklist_data)

        assert duplicate_response.status_code == status.HTTP_409_CONFLICT

    async def test_create_checklist_validation_error(self, client):
        """Test validation error returns 422."""
        checklist_data = {
            "id": "CL-INVALID",
            "title": "",  # Empty title should fail validation
        }

        response = await client.post("/api/v1/checklists", json=checklist_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_template_checklist(self, client):
        """Test creating a checklist template."""
        template_data = {
            "id": "CL-TEMPLATE-001",
            "title": "Template Checklist",
            "is_template": True,
            "items": [
                {"id": "CLI-T-001", "order": 1, "title": "Template Item 1"},
                {"id": "CLI-T-002", "order": 2, "title": "Template Item 2"},
            ],
        }

        response = await client.post("/api/v1/checklists", json=template_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_template"] is True

    async def test_create_from_template(self, client):
        """Test creating a checklist from a template."""
        # Create template
        template_data = {
            "id": "CL-TMPL-001",
            "title": "Template",
            "is_template": True,
            "items": [
                {"id": "CLI-T-001", "order": 1, "title": "Template Item"},
            ],
        }
        await client.post("/api/v1/checklists", json=template_data)

        # Create from template
        response = await client.post(
            "/api/v1/checklists/from-template?"
            "template_id=CL-TMPL-001&title=New%20Checklist"
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["template_id"] == "CL-TMPL-001"
        assert data["is_template"] is False

    async def test_complete_checklist(self, client):
        """Test completing a checklist."""
        # Create checklist with completed items
        checklist_data = {
            "id": "CL-COMPLETE-001",
            "title": "Complete Test",
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Complete checklist
        response = await client.post("/api/v1/checklists/CL-COMPLETE-001/complete")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_archive_checklist(self, client):
        """Test archiving a checklist."""
        # Create checklist
        checklist_data = {
            "id": "CL-ARCHIVE-001",
            "title": "Archive Test",
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Archive checklist
        response = await client.post("/api/v1/checklists/CL-ARCHIVE-001/archive")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "archived"

    async def test_check_item(self, client):
        """Test checking a checklist item."""
        # Create checklist with item
        checklist_data = {
            "id": "CL-CHECK-001",
            "title": "Check Test",
            "items": [{"id": "CLI-001", "order": 1, "title": "Item 1"}],
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Check item
        response = await client.post(
            "/api/v1/checklists/CL-CHECK-001/items/CLI-001/check"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = next(i for i in data["items"] if i["id"] == "CLI-001")
        assert item["status"] == "completed"

    async def test_uncheck_item(self, client):
        """Test unchecking a checklist item."""
        # Create checklist with item
        checklist_data = {
            "id": "CL-UNCHECK-001",
            "title": "Uncheck Test",
            "items": [{"id": "CLI-001", "order": 1, "title": "Item 1", "status": "completed"}],
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Uncheck item
        response = await client.post(
            "/api/v1/checklists/CL-UNCHECK-001/items/CLI-001/uncheck"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = next(i for i in data["items"] if i["id"] == "CLI-001")
        assert item["status"] == "pending"

    async def test_block_item(self, client):
        """Test blocking a checklist item."""
        # Create checklist with item
        checklist_data = {
            "id": "CL-BLOCK-001",
            "title": "Block Test",
            "items": [{"id": "CLI-001", "order": 1, "title": "Item 1"}],
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Block item
        response = await client.post(
            "/api/v1/checklists/CL-BLOCK-001/items/CLI-001/block?reason=Waiting%20on%20deps"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = next(i for i in data["items"] if i["id"] == "CLI-001")
        assert item["status"] == "blocked"

    async def test_unblock_item(self, client):
        """Test unblocking a checklist item."""
        # Create checklist with blocked item
        checklist_data = {
            "id": "CL-UNBLOCK-001",
            "title": "Unblock Test",
            "items": [{"id": "CLI-001", "order": 1, "title": "Item 1", "status": "blocked"}],
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Unblock item
        response = await client.post(
            "/api/v1/checklists/CL-UNBLOCK-001/items/CLI-001/unblock"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = next(i for i in data["items"] if i["id"] == "CLI-001")
        assert item["status"] == "pending"

    async def test_add_item_to_checklist(self, client):
        """Test adding an item to a checklist."""
        # Create checklist
        checklist_data = {
            "id": "CL-ADDITEM-001",
            "title": "Add Item Test",
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Add item
        item_data = {
            "title": "New Item",
            "priority": "high",
        }
        response = await client.post(
            "/api/v1/checklists/CL-ADDITEM-001/items", json=item_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "New Item"
        assert data["items"][0]["priority"] == "high"

    async def test_remove_item_from_checklist(self, client):
        """Test removing an item from a checklist."""
        # Create checklist with items
        checklist_data = {
            "id": "CL-REMOVE-001",
            "title": "Remove Item Test",
            "items": [
                {"id": "CLI-001", "order": 1, "title": "Item 1"},
                {"id": "CLI-002", "order": 2, "title": "Item 2"},
            ],
        }
        await client.post("/api/v1/checklists", json=checklist_data)

        # Remove item
        response = await client.delete(
            "/api/v1/checklists/CL-REMOVE-001/items/CLI-001"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == "CLI-002"

    async def test_search_checklists(self, client):
        """Test searching checklists with filters."""
        # Create checklists with different properties
        cl1 = {
            "id": "CL-SEARCH-001",
            "title": "Search Test 1",
            "task_id": "T-SEARCH",
        }
        cl2 = {
            "id": "CL-SEARCH-002",
            "title": "Search Test 2",
            "task_id": "T-OTHER",
        }
        await client.post("/api/v1/checklists", json=cl1)
        await client.post("/api/v1/checklists", json=cl2)

        # Search by task
        response = await client.get("/api/v1/checklists/search?task_id=T-SEARCH")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_templates(self, client):
        """Test getting checklist templates."""
        # Create template
        template_data = {
            "id": "CL-TMPL-LIST-001",
            "title": "Template List Test",
            "is_template": True,
        }
        await client.post("/api/v1/checklists", json=template_data)

        # Get templates
        response = await client.get("/api/v1/checklists/templates")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_incomplete_checklists(self, client):
        """Test getting incomplete checklists."""
        response = await client.get("/api/v1/checklists/incomplete")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_get_checklist_stats(self, client):
        """Test getting checklist statistics."""
        response = await client.get("/api/v1/checklists/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
