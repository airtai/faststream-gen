from typing import Dict, List

from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import Context, ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker


class CryptoPrice(BaseModel):
    price: NonNegativeFloat = Field(
        ..., examples=[50000], description="Current price of the cryptocurrency"
    )
    crypto_currency: str = Field(
        ..., examples=["BTC"], description="Cryptocurrency symbol"
    )


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


publisher = broker.publisher("price_mean")


@app.on_startup
async def app_setup(context: ContextRepo):
    message_history: Dict[str, List[float]] = {}
    context.set_global("message_history", message_history)


@broker.subscriber("new_crypto_price")
async def on_new_crypto_price(
    msg: CryptoPrice,
    logger: Logger,
    message_history: Dict[str, List[float]] = Context(),
    key: bytes = Context("message.raw_message.key"),
) -> None:
    logger.info(f"New crypto price {msg=}")

    crypto_key = key.decode("utf-8")
    if crypto_key not in message_history:
        message_history[crypto_key] = []

    message_history[crypto_key].append(msg.price)

    if len(message_history[crypto_key]) > 100:
        message_history[crypto_key] = message_history[crypto_key][-100:]

    if len(message_history[crypto_key]) >= 3:
        price_mean = sum(message_history[crypto_key][-3:]) / 3
        await publisher.publish(price_mean, key=key)