import asyncio
import json
from datetime import datetime

import aiohttp

from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


class CryptoPrice(BaseModel):
    price: NonNegativeFloat = Field(
        ..., examples=[50000.0], description="Current price of cryptocurrency in USD"
    )
    crypto_currency: str = Field(
        ..., examples=["BTC"], description="The cryptocurrency"
    )

publisher = broker.publisher("new_crypto_price")

async def fetch_crypto_price(
    url: str, crypto_currency: str, logger: Logger, context: ContextRepo, time_interval: int = 2
) -> None:
    # Always use context: ContextRepo for storing app_is_running variable
    while context.get("app_is_running"):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data["data"]["amount"]
                    new_crypto_price = CryptoPrice(
                        price=price, crypto_currency=crypto_currency
                    )
                    await publisher.publish(
                        new_crypto_price,
                        key=crypto_currency.encode("utf-8"),
                    )
                else:
                    logger.warning(
                        f"Failed API request {url} at time {datetime.now()}"
                    )

        await asyncio.sleep(time_interval)


@app.on_startup
async def app_setup(context: ContextRepo):
    context.set_global("app_is_running", True)


@app.on_shutdown
async def shutdown(context: ContextRepo):
    context.set_global("app_is_running", False)

    # Get all the running tasks and wait them to finish
    fetch_tasks = context.get("fetch_tasks")
    await asyncio.gather(*fetch_tasks)


@app.after_startup
async def publish_crypto_price(logger: Logger, context: ContextRepo):
    logger.info("Starting publishing:")

    cryptocurrencies = [("Bitcoin", "BTC"), ("Ethereum", "ETH")]
    fetch_tasks = [
        asyncio.create_task(
            fetch_crypto_price(
                f"https://api.coinbase.com/v2/prices/{crypto_currency}-USD/spot",
                crypto_currency,
                logger,
                context,
            )
        )
        for _, crypto_currency in cryptocurrencies
    ]
    # you need to save asyncio tasks so you can wait them to finish at app shutdown (the function with @app.on_shutdown function)
    context.set_global("fetch_tasks", fetch_tasks)