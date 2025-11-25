# =============================================================================
# ODIN v7.0 - Unit Tests: Message Bus
# =============================================================================

import pytest
import json
import time

from agents.shared.message_bus import (
    Message,
    MessagePriority,
    MessageBus,
)

# Check if redis is available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message(
            type="task",
            source="agent-1",
            payload={"data": "value"},
        )

        assert msg.type == "task"
        assert msg.source == "agent-1"
        assert msg.payload == {"data": "value"}
        assert msg.target == "*"  # Default
        assert msg.priority == MessagePriority.NORMAL
        assert msg.id is not None

    def test_message_with_all_fields(self):
        """Test message with all fields specified."""
        msg = Message(
            type="task",
            source="agent-1",
            target="agent-2",
            payload={"data": "value"},
            priority=MessagePriority.HIGH,
            correlation_id="corr-123",
            ttl=7200,
        )

        assert msg.target == "agent-2"
        assert msg.priority == MessagePriority.HIGH
        assert msg.correlation_id == "corr-123"
        assert msg.ttl == 7200

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message(
            type="task",
            source="agent-1",
            payload={"key": "value"},
        )

        data = msg.to_dict()

        assert data["type"] == "task"
        assert data["source"] == "agent-1"
        assert json.loads(data["payload"]) == {"key": "value"}
        assert data["priority"] == MessagePriority.NORMAL.value

    def test_message_from_dict(self):
        """Test message deserialization."""
        data = {
            "id": "msg-123",
            "type": "result",
            "source": "agent-1",
            "target": "agent-2",
            "payload": json.dumps({"result": "success"}),
            "priority": "2",
            "correlation_id": "corr-456",
            "timestamp": "1234567890.0",
            "ttl": "3600",
        }

        msg = Message.from_dict(data)

        assert msg.id == "msg-123"
        assert msg.type == "result"
        assert msg.source == "agent-1"
        assert msg.target == "agent-2"
        assert msg.payload == {"result": "success"}
        assert msg.priority == MessagePriority.HIGH
        assert msg.correlation_id == "corr-456"

    def test_message_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        original = Message(
            type="test",
            source="src",
            target="dst",
            payload={"nested": {"data": [1, 2, 3]}},
            priority=MessagePriority.CRITICAL,
            correlation_id="corr-789",
        )

        data = original.to_dict()
        restored = Message.from_dict(data)

        assert restored.type == original.type
        assert restored.source == original.source
        assert restored.target == original.target
        assert restored.payload == original.payload
        assert restored.priority == original.priority
        assert restored.correlation_id == original.correlation_id


class TestMessagePriority:
    """Test MessagePriority enum."""

    def test_priority_values(self):
        """Test priority ordering."""
        assert MessagePriority.LOW.value == 0
        assert MessagePriority.NORMAL.value == 1
        assert MessagePriority.HIGH.value == 2
        assert MessagePriority.CRITICAL.value == 3

    def test_priority_comparison(self):
        """Test priority can be compared."""
        assert MessagePriority.LOW.value < MessagePriority.NORMAL.value
        assert MessagePriority.CRITICAL.value > MessagePriority.HIGH.value


class TestMessageBusInitialization:
    """Test MessageBus initialization (without Redis)."""

    def test_bus_creation(self):
        """Test bus can be created."""
        bus = MessageBus(
            redis_url="redis://localhost:6379",
            stream_prefix="test:",
            consumer_group="test-group",
        )

        assert bus.redis_url == "redis://localhost:6379"
        assert bus.stream_prefix == "test:"
        assert bus.consumer_group == "test-group"

    def test_stream_name(self):
        """Test stream name generation."""
        bus = MessageBus(stream_prefix="odin:")

        assert bus._stream_name("tasks") == "odin:tasks"
        assert bus._stream_name("results") == "odin:results"

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="redis package not installed")
    def test_subscribe_handler(self):
        """Test handler subscription."""
        bus = MessageBus()
        handler_called = []

        def handler(msg):
            handler_called.append(msg)

        bus.subscribe("channel", handler, message_type="task")

        assert "channel:task" in bus._handlers
        assert handler in bus._handlers["channel:task"]

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="redis package not installed")
    def test_subscribe_wildcard(self):
        """Test wildcard subscription."""
        bus = MessageBus()

        def handler(msg):
            pass

        bus.subscribe("channel", handler)  # No message_type = wildcard

        assert "channel:*" in bus._handlers
