from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import ContextRepo, FastStream, Logger
from faststream.kafka import KafkaBroker

import requests
import asyncio

class CryptoPrice(BaseModel):
    price: NonNegativeFloat = Field(..., description="Current price of the cryptocurrency")
    currency: str = Field(..., description="Currency of the price")

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

new_data_publisher = broker.publisher("new_data")

async def fetch_and_publish_crypto_price(
    url: str,
    key: str,
    logger: Logger,
    context: ContextRepo,
    time_interval: int = 2,
) -> None:
    while context.get("app_is_running"):
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            price = data["data"]["amount"]
            currency = data["data"]["base"]
            crypto_price = CryptoPrice(price=price, currency=currency)
            await new_data_publisher.publish(crypto_price, key=key.encode("utf-8"))
        else:
            logger.warning(f"Failed to fetch data from {url}")
        await asyncio.sleep(time_interval)


@app.on_startup
async def app_setup(context: ContextRepo):
    context.set_global("app_is_running", True)


@app.on_shutdown
async def app_shutdown(context: ContextRepo):
    context.set_global("app_is_running", False)


@app.after_startup
async def publish_crypto_prices(logger: Logger, context: ContextRepo):
    logger.info("Starting publishing:")

    bitcoin_url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    ethereum_url = "https://api.coinbase.com/v2/prices/ETH-USD/spot"

    publish_tasks = [
        asyncio.create_task(
            fetch_and_publish_crypto_price(bitcoin_url, "BTC", logger, context)
        ),
        asyncio.create_task(
            fetch_and_publish_crypto_price(ethereum_url, "ETH", logger, context)
        ),
    ]
    context.set_global("publish_tasks", publish_tasks)
