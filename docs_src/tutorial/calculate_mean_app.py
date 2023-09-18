from typing import Dict, List

from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import Context, ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


class CryptoPrice(BaseModel):
    price: NonNegativeFloat = Field(
        ..., examples=[50000], description="Current price of the cryptocurrency"
    )
    crypto_currency: str = Field(
        ..., examples=["BTC"], description="Cryptocurrency symbol"
    )


publisher = broker.publisher("price_mean")


@app.on_startup
async def app_setup(context: ContextRepo):
    message_history: Dict[str, List[float]] = {}
    context.set_global("message_history", message_history)


@broker.subscriber("new_data")
async def on_new_data(
    msg: CryptoPrice,
    logger: Logger,
    message_history: Dict[str, List[float]] = Context(),
    key: bytes = Context("message.raw_message.key"),
) -> None:
    logger.info(f"New data received: {msg=}")

    partition_key = key.decode("utf-8")
    if partition_key not in message_history:
        message_history[partition_key] = []

    message_history[partition_key].append(msg.price)

    if len(message_history[partition_key]) > 100:
        message_history[partition_key].pop(0)

    if len(message_history[partition_key]) >= 3:
        price_mean = sum(message_history[partition_key][-3:]) / 3
        await publisher.publish(price_mean, key=key)
