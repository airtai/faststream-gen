import pytest
import numpy as np
from faststream import Context
from faststream.kafka import TestKafkaBroker

from app.application import PriceData, broker, on_new_data, prices

@broker.subscriber("price_mean")
async def on_price_mean(msg: float, key: bytes = Context("message.raw_message.key")):
    pass

@pytest.mark.asyncio
async def test_price_mean_calculation():
    async with TestKafkaBroker(broker):
        for i in range(1, 12):
            await broker.publish(PriceData(price=i, currency="USD"), "new_data", key=b"BTC")

        on_new_data.mock.assert_called_with(dict(PriceData(price=11, currency="USD")))
        on_price_mean.mock.assert_called_with(6.5)
        assert len(prices) == 11
        assert prices[-1] == 11
        assert prices[0] == 1
        assert pytest.approx(np.mean(prices[-10:]), 0.001) == 6.5