from datetime import datetime

import pytest

from faststream._compat import model_to_jsonable
from faststream.kafka import TestKafkaBroker

from .app import StudentQuery, broker, on_student_query


@broker.subscriber("finance_department")
async def on_finance_department(msg: StudentQuery) -> None:
    pass


@broker.subscriber("academic_department")
async def on_academic_department(msg: StudentQuery) -> None:
    pass


@broker.subscriber("admissions_department")
async def on_admissions_department(msg: StudentQuery) -> None:
    pass


@broker.subscriber("unclassified_query")
async def on_unclassified_query(msg: StudentQuery) -> None:
    pass


@pytest.mark.asyncio
async def test_message_published_to_correct_topic():
    async with TestKafkaBroker(broker):
        time = datetime.now()
        await broker.publish(
            StudentQuery(
                student_id=1,
                department="admissions_department",
                query="Help me with...",
                time=time,
            ),
            "student_query",
        )
        student_query_json = model_to_jsonable(
            StudentQuery(
                student_id=1,
                department="admissions_department",
                query="Help me with...",
                time=time,
            )
        )

        on_student_query.mock.assert_called_with(student_query_json)
        on_admissions_department.mock.assert_called_with(student_query_json)

        on_finance_department.mock.assert_not_called()
        on_academic_department.mock.assert_not_called()
        on_unclassified_query.mock.assert_not_called()
