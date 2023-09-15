from typing import Dict, List

from pydantic import BaseModel, Field

from faststream import Context, ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker

class NewData(BaseModel):
    price: float = Field(
        ..., examples=[1000], description="Current price of the crypto"
    )
    currency: str = Field(
        ..., examples=["BTC"], description="Currency of the price"
    )

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

to_price_mean = broker.publisher("price_mean")

@app.on_startup
async def app_setup(context: ContextRepo):
    message_history: Dict[str, List[float]] = {}
    context.set_global("message_history", message_history)

@broker.subscriber("new_data")
async def on_new_data(
    msg: NewData,
    logger: Logger,
    context: ContextRepo,
    key: bytes = Context("message.raw_message.key"),
) -> None:
    logger.info(f"{msg=}")

    message_history = context.get("message_history")

    partition_key = key.decode("utf-8")
    if partition_key not in message_history:
        message_history[partition_key] = []

    message_history[partition_key].append(msg.price)
    context.set_global("message_history", message_history)

    price_mean = sum(message_history[partition_key][-3:]) / 3
    await to_price_mean.publish(price_mean, key=key)
