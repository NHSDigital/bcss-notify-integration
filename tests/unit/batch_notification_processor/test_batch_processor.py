from batch_processor import BatchProcessor
import oracle_database
from recipient import Recipient
import pytest
import re
from unittest.mock import MagicMock, patch
import uuid
import database


@pytest.fixture
def batch_id():
    return str(uuid.uuid4())


@pytest.fixture
def plan_id():
    return str(uuid.uuid4())


@pytest.fixture
def recipients():
    return [
        Recipient(("0000000000", None, None, None, "requested")),
        Recipient(("1111111111", None, None, None, "requested")),
    ]


@patch("batch_processor.oracle_database", autospec=True)
@patch("oracle_database.database")
class TestBatchProcessor:
    def test_get_recipients(self, mock_database, mock_oracle_database, recipients):
        mock_oracle_database.get_recipients.return_value = recipients
        subject = BatchProcessor(batch_id)
        subject.generate_message_reference = MagicMock(
            side_effect=["message_reference_0", "message_reference_1"])

        recipients = subject.get_recipients()

        assert len(recipients) == 2

        assert recipients[0].nhs_number == "0000000000"
        assert recipients[0].message_id == "message_reference_0"
        assert recipients[0].message_status == "requested"

        assert recipients[1].nhs_number == "1111111111"
        assert recipients[1].message_id == "message_reference_1"
        assert recipients[1].message_status == "requested"

    def test_null_recipients(self, mock_database, mock_oracle_database, batch_id):
        mock_fetch_recipients = mock_oracle_database.get_recipients
        mock_fetch_recipients.return_value = None

        subject = BatchProcessor(batch_id)

        with pytest.raises(Exception) as exc_info:
            subject.get_recipients()

        assert str(exc_info.value) == "Failed to fetch recipients."
        assert mock_fetch_recipients.call_count == 1

    def test_get_routing_plan_id(self, mock_database, mock_oracle_database, batch_id):
        subject = BatchProcessor(batch_id)

        plan_id = str(uuid.uuid4())

        mock_fetch_routing_plan_id = mock_oracle_database.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        routing_plan_id = mock_oracle_database.get_routing_plan_id(batch_id)

        assert routing_plan_id == plan_id
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_null_routing_plan_id(self, mock_database, mock_oracle_database, batch_id):
        subject = BatchProcessor(batch_id)

        plan_id = None

        mock_fetch_routing_plan_id = mock_oracle_database.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        with pytest.raises(Exception) as exc_info:
            subject.get_routing_plan_id()

        assert str(exc_info.value) == "Failed to fetch routing plan ID."
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_mark_batch_as_sent(self, mock_database, mock_oracle_database, recipients):
        subject = BatchProcessor(batch_id)
        mock_update_message_status = mock_oracle_database.update_message_status

        subject.mark_batch_as_sent(recipients)

        assert mock_update_message_status.call_count == 2
        assert recipients[0].message_status == "sending"
        assert recipients[1].message_status == "sending"
        assert mock_update_message_status.call_args_list == [
            ((recipients[0],),),
            ((recipients[1],),),
        ]

    def test_generate_message_reference(self, mock_database, mock_oracle_database):
        subject = BatchProcessor(batch_id)

        message_reference = subject.generate_message_reference()

        assert isinstance(message_reference, str)
        assert len(message_reference) == 36
        assert re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", message_reference)
        for _ in range(100):
            assert message_reference != subject.generate_message_reference()
