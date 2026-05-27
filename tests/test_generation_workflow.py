import pytest
from unittest.mock import AsyncMock

from src.models.config import LLMConfig
from src.core.generation_workflow import GenerationWorkflow

@pytest.fixture
def llm_config():
    return LLMConfig(
        backend="vertex",
        model_id="gemini-2.5-flash",
        temperature=0.7,
    )

@pytest.mark.asyncio
async def test_generation_workflow_immediate_approval(mocker, llm_config):
    """Test that the workflow exits early if the evaluator immediately approves."""
    mock_run_agent = mocker.patch("src.core.generation_workflow.run_agent", new_callable=AsyncMock)
    
    # Define what the mock should return on successive calls:
    # 1. Writer -> initial draft
    # 2. Evaluator -> "APPROVED"
    mock_run_agent.side_effect = [
        "This is the initial draft.",
        "The summary looks great. APPROVED",
    ]
    
    workflow = GenerationWorkflow(llm_config)
    
    result = await workflow.process_document(
        document_id="doc123",
        filename="test.md",
        body="This is some source text about testing.",
        max_revisions=2
    )
    
    assert result == "This is the initial draft."
    assert mock_run_agent.call_count == 2
    
    # Verify the correct agents were called
    writer_call_kwargs = mock_run_agent.call_args_list[0].kwargs
    assert "session_id" in writer_call_kwargs
    assert writer_call_kwargs["session_id"].startswith("writer_")
    
    evaluator_call_kwargs = mock_run_agent.call_args_list[1].kwargs
    assert "session_id" in evaluator_call_kwargs
    assert evaluator_call_kwargs["session_id"].startswith("evaluator_")


@pytest.mark.asyncio
async def test_generation_workflow_with_revision(mocker, llm_config):
    """Test that the workflow loops to the editor if the evaluator critiques the draft."""
    mock_run_agent = mocker.patch("src.core.generation_workflow.run_agent", new_callable=AsyncMock)
    
    # Define what the mock should return on successive calls:
    # 1. Writer -> initial draft
    # 2. Evaluator -> Critique
    # 3. Editor -> Revised draft
    # 4. Evaluator -> APPROVED
    mock_run_agent.side_effect = [
        "This is the initial draft.",
        "CRITIQUE: Needs more detail.",
        "This is the revised draft with more detail.",
        "APPROVED"
    ]
    
    workflow = GenerationWorkflow(llm_config)
    
    result = await workflow.process_document(
        document_id="doc123",
        filename="test.md",
        body="This is some source text about testing.",
        max_revisions=2
    )
    
    assert result == "This is the revised draft with more detail."
    assert mock_run_agent.call_count == 4
    
    call_sessions = [call.kwargs.get("session_id", "") for call in mock_run_agent.call_args_list]
    assert call_sessions[0] == "writer_doc123"
    assert call_sessions[1] == "evaluator_doc123_0"
    assert call_sessions[2] == "editor_doc123_0"
    assert call_sessions[3] == "evaluator_doc123_1"


@pytest.mark.asyncio
async def test_generation_workflow_max_revisions_reached(mocker, llm_config):
    """Test that the workflow terminates when max_revisions is reached, even without approval."""
    mock_run_agent = mocker.patch("src.core.generation_workflow.run_agent", new_callable=AsyncMock)
    
    # Define what the mock should return on successive calls:
    # 1. Writer -> initial draft
    # 2. Evaluator -> Critique (rev 0)
    # 3. Editor -> Revised draft 1 (rev 0)
    # 4. Evaluator -> Critique (rev 1)
    # 5. Editor -> Revised draft 2 (rev 1)
    # Since max_revisions=2, it should stop here.
    mock_run_agent.side_effect = [
        "Initial draft.",
        "Needs work.",
        "Revised draft 1.",
        "Still needs work.",
        "Revised draft 2.",
    ]
    
    workflow = GenerationWorkflow(llm_config)
    
    result = await workflow.process_document(
        document_id="doc123",
        filename="test.md",
        body="This is some source text about testing.",
        max_revisions=2
    )
    
    assert result == "Revised draft 2."
    assert mock_run_agent.call_count == 5
