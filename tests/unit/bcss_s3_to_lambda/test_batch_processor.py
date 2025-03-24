import uuid
import pytest
from batch_processor import BatchProcessor
from oracle.oracle import DatabaseFetchError, get_routing_plan_id, get_recipients
from unittest.mock import MagicMock, patch


def test_get_recipients(
    mock_get_recipients,
    mock_get_connection,
    mock_connection,
    batch_id,
    recipients,
):
    mock_get_connection.return_value = mock_connection
    mock_get_recipients.return_value = recipients
    subject = BatchProcessor(batch_id)
    subject.generate_message_reference = MagicMock(
        side_effect=["message_reference_0", "message_reference_1"]
    )

    recipients = mock_get_recipients()

    assert len(recipients) == 2

    assert recipients[0].nhs_number == "0000000000"
    assert recipients[0].message_reference == "message_reference_0"
    assert recipients[0].message_status == "REQUESTED"

    assert recipients[1].nhs_number == "1111111111"
    assert recipients[1].message_reference == "message_reference_1"
    assert recipients[1].message_status == "REQUESTED"


def test_null_recipients(mock_batch_get_recipients, batch_id):
    subject = BatchProcessor(batch_id)

    mock_fetch_recipients = mock_batch_get_recipients
    mock_fetch_recipients.return_value = None

    with pytest.raises(DatabaseFetchError) as exc_info:
        subject.get_recipients()

    assert str(exc_info.value) == "Failed to fetch recipients."
    assert mock_fetch_recipients.called


def test_get_routing_plan_id(
    mock_get_connection,
    mock_connection,
    mock_batch_get_routing_plan_id,
    batch_id,
):
    mock_get_connection.return_value = mock_connection
    subject = BatchProcessor(batch_id)

    plan_id = str(uuid.uuid4())

    mock_fetch_routing_plan_id = mock_batch_get_routing_plan_id
    mock_fetch_routing_plan_id.return_value = plan_id

    routing_plan_id = subject.get_routing_plan_id()

    assert routing_plan_id == plan_id
    assert mock_fetch_routing_plan_id.call_count == 1


def test_null_routing_plan_id(
    mock_get_connection, mock_connection, mock_batch_get_routing_plan_id, batch_id
):
    mock_get_connection.return_value = mock_connection
    subject = BatchProcessor(batch_id)

    plan_id = None

    mock_fetch_routing_plan_id = mock_batch_get_routing_plan_id
    mock_fetch_routing_plan_id.return_value = plan_id

    with pytest.raises(DatabaseFetchError) as exc_info:
        subject.get_routing_plan_id()

    assert str(exc_info.value) == "Failed to fetch routing plan ID."
    assert mock_fetch_routing_plan_id.call_count == 1
