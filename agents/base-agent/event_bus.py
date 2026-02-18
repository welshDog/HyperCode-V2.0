import redis
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Generator

logger = logging.getLogger("AgentEventBus")

class AgentEventBus:
    """
    Redis-based Event Bus for Agents.
    """
    def __init__(self, redis_url: str, agent_name: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.agent_name = agent_name

    def publish(self, topic: str, event_type: str, payload: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish an event to the bus.
        """
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender_id": self.agent_name,
            "message_type": event_type,
            "payload": payload,
            "correlation_id": correlation_id
        }
        
        try:
            self.redis.publish(topic, json.dumps(message))
            logger.debug(f"Published {event_type} to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    def subscribe(self, topic: str) -> Generator[Dict[str, Any], None, None]:
        """
        Subscribe to a topic and yield messages.
        """
        pubsub = self.redis.pubsub()
        pubsub.subscribe(topic)
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        yield json.loads(message["data"])
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode message from {topic}")
        finally:
            pubsub.unsubscribe(topic)
            pubsub.close()
