from datetime import datetime

import pytest
from freezegun import freeze_time

from faststream import Context
from faststream._compat import model_to_jsonable
from faststream.kafka import TestKafkaBroker

from .app import Point, broker, on_input_data


@broker.subscriber("output_data")
async def on_output_data(msg: Point, key: bytes = Context("message.raw_message.key")):
    pass


# Feeze time so the datetime always uses the same time
@freeze_time("2023-01-01")
@pytest.mark.asyncio
async def test_point_was_incremented():
    async with TestKafkaBroker(broker):
        time = datetime.now()
        await broker.publish(Point(x=1.0, y=2.0, time=time), "input_data", key=b"key")

        point_json = model_to_jsonable(Point(x=1.0, y=2.0, time=time))
        on_input_data.mock.assert_called_with(point_json)

        point_json = model_to_jsonable(Point(x=2.0, y=3.0, time=time))
        on_output_data.mock.assert_called_with(point_json)
