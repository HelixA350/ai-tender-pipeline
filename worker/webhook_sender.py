import asyncio
import logging
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
from api.config import settings

logger = logging.getLogger(__name__)

TOPIC = "extraction-results"
BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers


async def send_webhook(payload: dict, max_retries: int = 3) -> bool:
    target_url = payload.get("base_url") or settings.webhook_url
    if not target_url:
        logger.warning("No base_url provided and WEBHOOK_URL not set, skipping webhook")
        return False

    import httpx

    body = payload.get("result_json", payload)

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(target_url, json=body)
                resp.raise_for_status()
                logger.info(f"Webhook sent to {target_url}: {body}")
                return True
        except Exception as e:
            logger.error(f"Webhook attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
    return False


def main():
    logger.info(f"Starting webhook sender for topic '{TOPIC}'...")

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="webhook-senders",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    logger.info(f"Webhook sender started, listening to {TOPIC}")

    for message in consumer:
        payload = message.value
        logger.info(f"Received result for task {payload.get('result_json', {}).get('tender_id', '?')}")
        asyncio.run(send_webhook(payload))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
