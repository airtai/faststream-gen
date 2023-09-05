from pydantic import BaseModel, Field, NonNegativeFloat

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker


class DataBasic(BaseModel):
    data: NonNegativeFloat = Field(
        ..., examples=[0.5], description="Float data example"
    )


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.publisher("output_data")
@broker.subscriber("input_data")
async def on_input_data(msg: DataBasic, logger: Logger) -> DataBasic:
    """Processes a message from 'input_data' topic, increments 'data' attribute by 1, and sends it to 'output_data'.

    Instructions:
    1. Consume a message from 'input_data' topic.
    2. Create a new message object (do not directly modify the original).
    3. Increment 'data' attribute by 1 in the new message.
    4. Send the modified message to 'output_data' topic.

    """
    raise NotImplementedError()