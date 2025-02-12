from BCSSNotifyBatchProcessor import BCSSNotifyBatchProcessor
from OracleDatabase import OracleDatabase
import pytest
from unittest.mock import MagicMock
import uuid

# Fixtures: Things we don't want to repeatedly define.
# They also help keep the tests a bit less cluttered.
@pytest.fixture
def db_config():
    return {"dsn": "dsn", "password": "password", "user": "user"}


@pytest.fixture
def batch_id():
    return str(uuid.uuid4())


@pytest.fixture
def plan_id():
    return str(uuid.uuid4())


@pytest.fixture
def participants():
    return [
        ["0000000000", "message_reference_0"],
        ["1111111111", "message_reference_1"],
    ]


class TestBCSSNotifyBatchProcessor:
    # Test the get_participants method
    # We need to mock the OracleDatabase class and its methods but we can still test that they are called correctly.
    def test_get_participants(self, db_config, batch_id, plan_id, participants):
        subject = BCSSNotifyBatchProcessor(db_config)
        subject.db = MagicMock(spec=OracleDatabase)
        # We have to mock this because it also calls db.execute_query.
        # Ideally this method should not exist, we should just find a way to generate a unique ID.
        subject.generate_participants_message_reference = MagicMock(return_value=participants)

        # Mock the call to the database which returns the routing plan ID.
        mock_fetch_routing_plan_id = subject.db.call_function
        mock_fetch_routing_plan_id.return_value = plan_id

        # Mock the call to the database which returns the participants.
        mock_fetch_participants = subject.db.execute_query
        mock_fetch_participants.return_value = participants

        participants, routing_plan_id = subject.get_participants(batch_id)

        assert plan_id == routing_plan_id
        assert len(participants) == 2

        # Assert that the database methods were called correctly.
        assert mock_fetch_routing_plan_id.call_count == 1
        assert mock_fetch_routing_plan_id.call_args[0][0] == "PKG_NOTIFY_WRAP.f_get_next_batch"
        assert mock_fetch_routing_plan_id.call_args[0][2] == [batch_id]

        assert mock_fetch_participants.call_count == 1
        assert mock_fetch_participants.call_args[0][0] == "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id"
        assert mock_fetch_participants.call_args[0][1] == {"batch_id": batch_id}

        # Assert that the data was correctly returned.
        nhs_number, message_reference = participants[0]
        assert nhs_number == "0000000000"
        assert message_reference == "message_reference_0"

        nhs_number, message_reference = participants[1]
        assert nhs_number == "1111111111"
        assert message_reference == "message_reference_1"
