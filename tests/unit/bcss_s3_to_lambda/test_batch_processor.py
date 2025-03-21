import uuid
import pytest
from batch_processor import BatchProcessor
from oracle.oracle import DatabaseFetchError
from unittest.mock import MagicMock, patch


# Fixtures: Things we don't want to repeatedly define.
# They also help keep the tests a bit less cluttered.


class TestBatchProcessor:
    def test_get_recipients(
        self,
        mock_get_recipients,
        mock_oracledb_connect,
        batch_id,
        db_config,
        recipients,
    ):
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

    def test_null_recipients(self, mock_oracledb_connect, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        mock_fetch_recipients = subject.db.get_recipients
        mock_fetch_recipients.return_value = None

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_recipients()

        assert str(exc_info.value) == "Failed to fetch recipients."
        assert mock_fetch_recipients.call_count == 1

    def test_get_routing_plan_id(self, mock_oracledb_connect, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        plan_id = str(uuid.uuid4())

        mock_fetch_routing_plan_id = subject.db.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        routing_plan_id = subject.get_routing_plan_id()

        assert routing_plan_id == plan_id
        assert mock_fetch_routing_plan_id.call_count == 1

    def test_null_routing_plan_id(self, mock_oracledb_connect, db_config, batch_id):
        subject = BatchProcessor(batch_id, db_config)

        plan_id = None

        mock_fetch_routing_plan_id = subject.db.get_routing_plan_id
        mock_fetch_routing_plan_id.return_value = plan_id

        with pytest.raises(DatabaseFetchError) as exc_info:
            subject.get_routing_plan_id()

        assert str(exc_info.value) == "Failed to fetch routing plan ID."
        assert mock_fetch_routing_plan_id.call_count == 1
