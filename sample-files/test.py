import pytest
import asyncio

from faststream.kafka import TestKafkaBroker

from application import *


@pytest.mark.asyncio
async def test_base_app():
    @broker.subscriber("output_data")
    async def on_output_data(msg: DataBasic):
        pass

    async with TestKafkaBroker(broker) as tester:
        await tester.publish(DataBasic(data=0.2), "input_data")

        on_input_data.mock.assert_called_with(dict(DataBasic(data=0.2)))

        on_output_data.mock.assert_called_once_with(dict(DataBasic(data=1.2)))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_base_app())