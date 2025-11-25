# =============================================================================
# ODIN v7.0 - Test Configuration
# =============================================================================

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "content": "Test response",
        "model": "test-model",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
    }
