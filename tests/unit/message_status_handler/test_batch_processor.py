from batch_processor import BatchProcessor
from oracle_database import OracleDatabase, DatabaseFetchError
from recipient import Recipient
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
def recipients():
    return [
        Recipient(("0000000000", None, None, None, "REQUESTED")),
        Recipient(("1111111111", None, None, None, "REQUESTED")),
    ]


@patch("batch_processor.OracleDatabase", autospec=True)
class TestBatchProcessor:
    def test_get_recipients(self, mock_oracle_database, db_config, recipients):
        mock_oracle_database.return_value.get_recipients.return_value = recipients
        subject = BatchProcessor(batch_id, db_config)
        subject.generate_message_reference = MagicMock(
            side_effect=["message_reference_0", "message_reference_1"])

        recipients = subject.get_recipients()

        assert len(recipients) == 2

        assert recipients[0].nhs_number == "0000000000"
        assert recipients[0].message_id == "message_reference_0"
        assert recipients[0].message_status == "REQUESTED"

        assert recipients[1].nhs_number == "1111111111"
        assert recipients[1].message_id == "message_reference_1"
        assert recipients[1].message_status == "REQUESTED"

    def test_null_recipients(self, mock_oracle_database, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        mock_fetch_recipients = subject.db.get_recipients
        mock_fetch_recipients.return_value = None

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_recipients()

        assert str(exc_info.value) == "Failed to fetch recipients."
        assert mock_fetch_recipients.call_count == 1

    def test_get_routing_plan_id(self, mock_oracle_database, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        plan_id = str(uuid.uuid4())

        mock_fetch_routing_plan_id = subject.db.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        routing_plan_id = subject.get_routing_plan_id()

        assert routing_plan_id == plan_id
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_null_routing_plan_id(self, mock_oracle_database, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        plan_id = None

        mock_fetch_routing_plan_id = subject.db.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_routing_plan_id()

        assert str(exc_info.value) == "Failed to fetch routing plan ID."
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_mark_batch_as_sent(self, mock_oracle_database, db_config, recipients):
        subject = BatchProcessor(batch_id, db_config)
        mock_update_message_status = subject.db.update_message_status

        subject.mark_batch_as_sent(recipients)

        assert mock_update_message_status.call_count == 2
        assert mock_update_message_status.call_args_list == [
            ((recipients[0],),),
            ((recipients[1],),),
        ]
