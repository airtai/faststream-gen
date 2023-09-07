from pydantic import BaseModel, Field

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker


class Employee(BaseModel):
    employee_name: str = Field(
        ..., examples=["John Doe"], description="Employee name"
    )
    age: int = Field(
        ..., examples=[30], description="Age"
    )
    location: str = Field(
        ..., examples=["New York"], description="Location"
    )
    experience: int = Field(
        ..., examples=[5], description="Experience in years"
    )


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.subscriber("new_joinee")
@broker.publisher("project_team")
@broker.publisher("admin_team")
async def on_new_joinee(msg: Employee, logger: Logger):
    logger.info(msg)
    return msg