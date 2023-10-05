import pytest

from faststream import Context, TestApp
from faststream.kafka import TestKafkaBroker

from app.application import CryptoPrice, app, broker


@broker.subscriber("new_crypto_price")
async def on_new_crypto_price(
    msg: CryptoPrice, key: bytes = Context("message.raw_message.key")
):
    pass


@pytest.mark.asyncio
async def test_fetch_crypto_price():
    async with TestKafkaBroker(broker):
        async with TestApp(app):
            await on_new_crypto_price.wait_call(2)
            on_new_crypto_price.mock.assert_called()