import pytest

from faststream import Context, TestApp
from faststream.kafka import TestKafkaBroker

from app.application import CryptoPrice, app, broker, on_new_crypto_price


@broker.subscriber("price_mean")
async def on_price_mean(msg: float, key: bytes = Context("message.raw_message.key")):
    pass


@pytest.mark.asyncio
async def test_app():
    async with TestKafkaBroker(broker):
        async with TestApp(app):
            await broker.publish(
                CryptoPrice(price=50000, crypto_currency="BTC"),
                "new_crypto_price",
                key=b"BTC",
            )
            on_new_crypto_price.mock.assert_called_with(
                dict(CryptoPrice(price=50000, crypto_currency="BTC"))
            )
            on_price_mean.mock.assert_not_called()

            await broker.publish(
                CryptoPrice(price=60000, crypto_currency="BTC"),
                "new_crypto_price",
                key=b"BTC",
            )
            on_new_crypto_price.mock.assert_called_with(
                dict(CryptoPrice(price=60000, crypto_currency="BTC"))
            )
            on_price_mean.mock.assert_not_called()

            await broker.publish(
                CryptoPrice(price=70000, crypto_currency="BTC"),
                "new_crypto_price",
                key=b"BTC",
            )
            on_new_crypto_price.mock.assert_called_with(
                dict(CryptoPrice(price=70000, crypto_currency="BTC"))
            )
            on_price_mean.mock.assert_called_with(60000.0)