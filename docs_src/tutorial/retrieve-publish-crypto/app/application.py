import asyncio
import json
from datetime import datetime

from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker
import requests

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

publisher = broker.publisher("new_crypto_price")


class CryptoPrice(BaseModel):
    price: NonNegativeFloat = Field(
        ..., examples=[50000.0], description="Current price of the cryptocurrency in USD"
    )
    crypto_currency: str = Field(
        ..., examples=["BTC"], description="Cryptocurrency symbol"
    )


@app.on_startup
async def app_setup(context: ContextRepo):
    context.set_global("app_is_running", True)


@app.on_shutdown
async def shutdown(context: ContextRepo):
    context.set_global("app_is_running", False)

    # Get all the running tasks and wait for them to finish
    publish_tasks = context.get("publish_tasks")
    await asyncio.gather(*publish_tasks)


async def fetch_and_publish_crypto_price(
    crypto_currency: str,
    logger: Logger,
    context: ContextRepo,
    time_interval: int = 2,
) -> None:
    # Always use context: ContextRepo for storing app_is_running variable
    while context.get("app_is_running"):
        url = f"https://api.coinbase.com/v2/prices/{crypto_currency}-USD/spot"
        response = requests.get(url)

        if response.status_code == 200:
            # read json response
            raw_data = json.loads(response.content)
            price = raw_data["data"]["amount"]

            new_crypto_price = CryptoPrice(
                price=price, crypto_currency=crypto_currency
            )
            key = crypto_currency.encode("utf-8")
            await publisher.publish(new_crypto_price, key=key)
        else:
            logger.warning(
                f"Failed API request {url} at time {datetime.now()}"
            )

        await asyncio.sleep(time_interval)


@app.after_startup
async def publish_crypto_price(logger: Logger, context: ContextRepo):
    logger.info("Starting publishing:")

    crypto_currencies = ["BTC", "ETH"]
    # start fetching and publishing crypto prices
    publish_tasks = [
        asyncio.create_task(
            fetch_and_publish_crypto_price(
                crypto_currency, logger, context
            )
        )
        for crypto_currency in crypto_currencies
    ]
    # you need to save asyncio tasks so you can wait for them to finish at app shutdown (the function with @app.on_shutdown function)
    context.set_global("publish_tasks", publish_tasks)