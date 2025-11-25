# =============================================================================
# ODIN v7.0 - Message Bus (Redis Streams)
# =============================================================================
# Inter-agent communication via Redis Streams
# Supports pub/sub, request/reply, and streaming patterns
# =============================================================================

from __future__ import annotations
import json
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, AsyncIterator
from enum import Enum

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Message:
    """
    Inter-agent message format.

    Attributes:
        id: Unique message identifier
        type: Message type (e.g., "task", "result", "event")
        source: Source agent ID
        target: Target agent ID (or "*" for broadcast)
        payload: Message data
        priority: Message priority
        correlation_id: For request/reply patterns
        timestamp: Unix timestamp
        ttl: Time-to-live in seconds
    """
    type: str
    source: str
    payload: Dict[str, Any]
    target: str = "*"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    ttl: int = 3600  # 1 hour default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "payload": json.dumps(self.payload),
            "priority": self.priority.value,
            "correlation_id": self.correlation_id or "",
            "timestamp": str(self.timestamp),
            "ttl": str(self.ttl),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        """Create Message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=data["type"],
            source=data["source"],
            target=data.get("target", "*"),
            payload=json.loads(data.get("payload", "{}")),
            priority=MessagePriority(int(data.get("priority", 1))),
            correlation_id=data.get("correlation_id") or None,
            timestamp=float(data.get("timestamp", time.time())),
            ttl=int(data.get("ttl", 3600)),
        )


class MessageBus:
    """
    Redis Streams-based message bus for inter-agent communication.

    Supports:
    - Pub/sub messaging
    - Request/reply patterns
    - Consumer groups for load balancing
    - Message persistence and replay
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "odin:",
        consumer_group: str = "odin-agents",
    ):
        """
        Initialize message bus.

        Args:
            redis_url: Redis connection URL
            stream_prefix: Prefix for stream names
            consumer_group: Consumer group name for this bus
        """
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.consumer_group = consumer_group
        self._redis = None
        self._consumer_id = str(uuid.uuid4())[:8]
        self._handlers: Dict[str, List[Callable]] = {}

    @property
    def redis(self):
        """Lazy Redis connection."""
        if self._redis is None:
            try:
                import redis
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
            except ImportError:
                raise RuntimeError("redis package required: pip install redis")
        return self._redis

    def _stream_name(self, channel: str) -> str:
        """Get full stream name for a channel."""
        return f"{self.stream_prefix}{channel}"

    def _ensure_consumer_group(self, stream: str):
        """Ensure consumer group exists for stream."""
        try:
            self.redis.xgroup_create(
                stream,
                self.consumer_group,
                id="0",
                mkstream=True
            )
        except Exception as e:
            # Group may already exist
            if "BUSYGROUP" not in str(e):
                raise

    def publish(
        self,
        channel: str,
        message: Message,
        maxlen: int = 10000
    ) -> str:
        """
        Publish message to a channel.

        Args:
            channel: Channel name
            message: Message to publish
            maxlen: Maximum stream length (for cleanup)

        Returns:
            Message ID in stream
        """
        stream = self._stream_name(channel)
        msg_dict = message.to_dict()

        message_id = self.redis.xadd(
            stream,
            msg_dict,
            maxlen=maxlen,
            approximate=True
        )

        logger.debug(f"Published message {message.id} to {stream}")
        return message_id

    def subscribe(
        self,
        channel: str,
        handler: Callable[[Message], None],
        message_type: Optional[str] = None
    ):
        """
        Subscribe to a channel.

        Args:
            channel: Channel name
            handler: Callback function for messages
            message_type: Optional filter by message type
        """
        key = f"{channel}:{message_type or '*'}"
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(handler)

        # Ensure consumer group exists
        stream = self._stream_name(channel)
        self._ensure_consumer_group(stream)

    def consume(
        self,
        channels: List[str],
        block: int = 5000,
        count: int = 10
    ) -> List[Message]:
        """
        Consume messages from channels.

        Args:
            channels: List of channel names
            block: Block timeout in milliseconds
            count: Maximum messages to return

        Returns:
            List of messages
        """
        streams = {self._stream_name(ch): ">" for ch in channels}

        # Ensure consumer groups exist
        for stream in streams.keys():
            self._ensure_consumer_group(stream)

        try:
            results = self.redis.xreadgroup(
                self.consumer_group,
                self._consumer_id,
                streams,
                count=count,
                block=block
            )
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            return []

        messages = []
        for stream_name, stream_messages in results or []:
            for msg_id, msg_data in stream_messages:
                try:
                    message = Message.from_dict(msg_data)
                    messages.append(message)

                    # Dispatch to handlers
                    self._dispatch(stream_name, message)

                    # Acknowledge message
                    self.redis.xack(stream_name, self.consumer_group, msg_id)
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")

        return messages

    def _dispatch(self, stream: str, message: Message):
        """Dispatch message to registered handlers."""
        channel = stream.replace(self.stream_prefix, "")

        # Try specific handler first
        key = f"{channel}:{message.type}"
        handlers = self._handlers.get(key, [])

        # Then wildcard handlers
        wildcard_key = f"{channel}:*"
        handlers.extend(self._handlers.get(wildcard_key, []))

        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Handler error for message {message.id}: {e}")

    def request(
        self,
        channel: str,
        message: Message,
        timeout: float = 30.0
    ) -> Optional[Message]:
        """
        Send request and wait for reply.

        Args:
            channel: Channel name
            message: Request message
            timeout: Timeout in seconds

        Returns:
            Reply message or None on timeout
        """
        # Create reply channel
        reply_channel = f"reply:{message.id}"
        reply_stream = self._stream_name(reply_channel)

        # Set correlation ID
        message.correlation_id = message.id

        # Publish request
        self.publish(channel, message)

        # Wait for reply
        start = time.time()
        while time.time() - start < timeout:
            try:
                results = self.redis.xread(
                    {reply_stream: "0"},
                    count=1,
                    block=1000
                )

                if results:
                    for _, messages in results:
                        for _, msg_data in messages:
                            reply = Message.from_dict(msg_data)
                            # Clean up reply stream
                            self.redis.delete(reply_stream)
                            return reply
            except Exception as e:
                logger.error(f"Error waiting for reply: {e}")

        logger.warning(f"Request {message.id} timed out")
        return None

    def reply(self, original: Message, response: Message):
        """
        Send reply to a request.

        Args:
            original: Original request message
            response: Response message
        """
        if not original.correlation_id:
            logger.warning("Cannot reply to message without correlation_id")
            return

        reply_channel = f"reply:{original.correlation_id}"
        response.correlation_id = original.correlation_id
        response.target = original.source

        self.publish(reply_channel, response)

    def close(self):
        """Close Redis connection."""
        if self._redis:
            self._redis.close()
            self._redis = None


class AsyncMessageBus:
    """
    Async version of MessageBus using aioredis.

    For use in async agent implementations.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "odin:",
        consumer_group: str = "odin-agents",
    ):
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.consumer_group = consumer_group
        self._redis = None
        self._consumer_id = str(uuid.uuid4())[:8]

    async def connect(self):
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis
            self._redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True
            )
        except ImportError:
            raise RuntimeError("redis[async] package required: pip install redis[async]")

    async def publish(self, channel: str, message: Message, maxlen: int = 10000) -> str:
        """Async publish."""
        stream = f"{self.stream_prefix}{channel}"
        return await self._redis.xadd(
            stream,
            message.to_dict(),
            maxlen=maxlen,
            approximate=True
        )

    async def consume(
        self,
        channels: List[str],
        block: int = 5000,
        count: int = 10
    ) -> AsyncIterator[Message]:
        """
        Async generator for consuming messages.

        Usage:
            async for message in bus.consume(["tasks"]):
                await process(message)
        """
        streams = {f"{self.stream_prefix}{ch}": ">" for ch in channels}

        # Ensure consumer groups
        for stream in streams.keys():
            try:
                await self._redis.xgroup_create(
                    stream,
                    self.consumer_group,
                    id="0",
                    mkstream=True
                )
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    raise

        while True:
            try:
                results = await self._redis.xreadgroup(
                    self.consumer_group,
                    self._consumer_id,
                    streams,
                    count=count,
                    block=block
                )

                for stream_name, messages in results or []:
                    for msg_id, msg_data in messages:
                        try:
                            message = Message.from_dict(msg_data)
                            yield message
                            await self._redis.xack(
                                stream_name,
                                self.consumer_group,
                                msg_id
                            )
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
                await self._redis.close()
                await self.connect()

    async def close(self):
        """Close async connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
