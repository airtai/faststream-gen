import pytest

from faststream import Context, TestApp
from faststream.kafka import TestKafkaBroker

from app.application import CryptoPrice, app, broker


@broker.subscriber("price_mean")
async def on_price_mean(
    msg: float, key: bytes = Context("message.raw_message.key")
):
    pass


@pytest.mark.asyncio
async def test_price_mean_calculation():
    async with TestKafkaBroker(broker):
        async with TestApp(app):
            await broker.publish(
                CryptoPrice(price=100, crypto_currency="BTC"),
                "new_data",
                key=b"partition_key",
            )
            await broker.publish(
                CryptoPrice(price=200, crypto_currency="BTC"),
                "new_data",
                key=b"partition_key",
            )
            await broker.publish(
                CryptoPrice(price=300, crypto_currency="BTC"),
                "new_data",
                key=b"partition_key",
            )
            await broker.publish(
                CryptoPrice(price=400, crypto_currency="BTC"),
                "new_data",
                key=b"partition_key",
            )
            await broker.publish(
                CryptoPrice(price=500, crypto_currency="BTC"),
                "new_data",
                key=b"partition_key",
            )

            on_price_mean.mock.assert_called_with(400.0)