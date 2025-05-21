import batch_processor
from batch_processor import RecipientsNotFoundError
from recipient import Recipient
import pytest
import re
from unittest.mock import MagicMock, patch
import uuid


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


@patch("batch_processor.oracle_database")
def test_next_batch(mock_oracle_database, recipients, batch_id, plan_id):
    mock_oracle_database.get_routing_plan_id.return_value = plan_id
    mock_oracle_database.get_recipients.return_value = recipients
    with patch("batch_processor.generate_reference") as mock_generate_reference:
        mock_generate_reference.return_value = batch_id

        result = batch_processor.next_batch()

    assert result == (batch_id, plan_id, recipients)
    assert mock_oracle_database.get_routing_plan_id.call_count == 1
    assert mock_oracle_database.get_recipients.call_count == 1
    assert mock_generate_reference.call_count == 3


@patch("batch_processor.oracle_database")
def test_next_batch_no_plan_id(mock_oracle_database, batch_id):
    mock_oracle_database.get_routing_plan_id.return_value = None
    with patch("batch_processor.generate_reference") as mock_generate_reference:
        mock_generate_reference.return_value = batch_id

        result = batch_processor.next_batch()

    assert result == (batch_id, None, None)
    assert mock_oracle_database.get_routing_plan_id.call_count == 1
    assert mock_oracle_database.get_recipients.call_count == 0
    assert mock_generate_reference.call_count == 1


@patch("batch_processor.oracle_database")
def test_get_recipients(mock_oracle_database, recipients, batch_id):
    mock_oracle_database.get_recipients.return_value = recipients
    with patch("batch_processor.generate_message_reference") as mock_generate_message_reference:
        mock_generate_message_reference.side_effect = ["message_reference_0", "message_reference_1"]

        recipients = batch_processor.get_recipients(batch_id)

    assert len(recipients) == 2

    assert recipients[0].nhs_number == "0000000000"
    assert recipients[0].message_id == "message_reference_0"
    assert recipients[0].message_status == "requested"

    assert recipients[1].nhs_number == "1111111111"
    assert recipients[1].message_id == "message_reference_1"
    assert recipients[1].message_status == "requested"


@patch("batch_processor.oracle_database")
def test_null_recipients(mock_oracle_database, batch_id):
    mock_fetch_recipients = mock_oracle_database.get_recipients
    mock_fetch_recipients.return_value = []

    assert batch_processor.get_recipients(batch_id) == []

    assert mock_fetch_recipients.call_count == 1


@patch("batch_processor.oracle_database")
def test_get_routing_plan_id(mock_oracle_database, batch_id):
    plan_id = str(uuid.uuid4())

    mock_fetch_routing_plan_id = mock_oracle_database.get_routing_plan_id
    mock_fetch_routing_plan_id.return_value = plan_id

    routing_plan_id = batch_processor.get_routing_plan_id(batch_id)

    assert routing_plan_id == plan_id
    assert mock_fetch_routing_plan_id.call_count == 1


@patch("batch_processor.oracle_database")
def test_null_routing_plan_id(mock_oracle_database, batch_id):
    mock_fetch_routing_plan_id = mock_oracle_database.get_routing_plan_id
    mock_fetch_routing_plan_id.return_value = None

    assert batch_processor.get_routing_plan_id(batch_id) is None


@patch("batch_processor.oracle_database")
def test_mark_batch_as_sent(mock_oracle_database, batch_id):
    mock_mark_batch_as_sent = mock_oracle_database.mark_batch_as_sent

    batch_processor.mark_batch_as_sent(batch_id)

    mock_mark_batch_as_sent.assert_called_once_with(batch_id)


def test_generate_message_reference():
    message_reference = batch_processor.generate_message_reference()

    assert isinstance(message_reference, str)
    assert len(message_reference) == 36
    assert re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", message_reference)
    for _ in range(100):
        assert message_reference != batch_processor.generate_message_reference()
