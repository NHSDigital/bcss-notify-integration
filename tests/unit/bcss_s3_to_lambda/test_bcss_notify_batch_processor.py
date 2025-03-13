from bcss_notify_batch_processor import BCSSNotifyBatchProcessor
from oracle_database import OracleDatabase, DatabaseFetchError
import pytest
from unittest.mock import MagicMock, patch
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


@patch("bcss_notify_batch_processor.OracleDatabase", autospec=True)
class TestBCSSNotifyBatchProcessor:
    # Test the get_participants method
    # We need to mock the OracleDatabase class and its methods but we can still test that they are called correctly.
    def test_get_participants(self, mock_oracle_database, db_config, batch_id, plan_id, participants):
        subject = BCSSNotifyBatchProcessor(batch_id, db_config)
        subject.db.get_set_of_participants = MagicMock(return_value=participants)

        assert len(participants) == 2

        # Assert that the data was correctly returned.
        nhs_number, message_reference = participants[0]
        assert nhs_number == "0000000000"
        assert message_reference == "message_reference_0"

        nhs_number, message_reference = participants[1]
        assert nhs_number == "1111111111"
        assert message_reference == "message_reference_1"

    def test_null_participants(self, mock_oracle_database, db_config, batch_id):
        subject = BCSSNotifyBatchProcessor(batch_id, db_config)

        mock_fetch_participants = subject.db.get_set_of_participants
        mock_fetch_participants.return_value = None

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_participants()

        assert str(exc_info.value) == "Failed to fetch participants."
        assert mock_fetch_participants.call_count == 1

    def test_get_routing_plan_id(self, mock_oracle_database, db_config, batch_id):
        subject = BCSSNotifyBatchProcessor(batch_id, db_config)

        plan_id = str(uuid.uuid4())

        mock_fetch_routing_plan_id = subject.db.get_next_batch
        mock_fetch_routing_plan_id.return_value = plan_id

        routing_plan_id = subject.get_routing_plan_id()

        assert routing_plan_id == plan_id
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_null_routing_plan_id(self, mock_oracle_database, db_config, batch_id):
        subject = BCSSNotifyBatchProcessor(batch_id, db_config)

        plan_id = None

        mock_fetch_routing_plan_id = subject.db.get_next_batch
        mock_fetch_routing_plan_id.return_value = plan_id

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_routing_plan_id()

        assert str(exc_info.value) == "Failed to fetch routing plan ID."
        assert mock_fetch_routing_plan_id.call_count == 1
