import pytest

from faststream.kafka import TestKafkaBroker

from application import *


@broker.subscriber("project_team")
async def on_project_team(msg: Employee):
    pass

@broker.subscriber("admin_team")
async def on_admin_team(msg: Employee):
    pass

@pytest.mark.asyncio
async def test_app():
    async with TestKafkaBroker(broker):
        await broker.publish(Employee(employee_name="John Doe", age=30, location="New York", experience=5), "new_joinee")

        on_new_joinee.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))
        on_project_team.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))
        on_admin_team.mock.assert_called_with(dict(Employee(employee_name="John Doe", age=30, location="New York", experience=5)))