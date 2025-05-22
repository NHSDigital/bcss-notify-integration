from unittest.mock import Mock, patch
import lambda_function
from recipient import Recipient


def test_lambda_handler():
    mock_batch_processor = Mock()
    lambda_function.batch_processor = mock_batch_processor
    mock_communication_management = Mock()
    lambda_function.CommunicationManagement = mock_communication_management

    recipients = [
        Recipient(("1234567890", "message_reference_0", "new")),
        Recipient(("0987654321", "message_reference_1", "new")),
    ]

    batch_id_1 = "b3b3b3b3-b3b3-b3b3-b3b3-b3b3b3b3b3b3"
    routing_plan_id_1 = "c2c2c2c2-c2c2-c2c2c2c2-c2c2c2c2c2c2"
    batch_id_2 = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"

    mock_batch_processor.next_batch = Mock(side_effect=[
        (batch_id_1, routing_plan_id_1, recipients),
        (batch_id_2, None, None),
    ])

    mock_response = Mock()
    mock_response.status_code = 201
    mock_communication_management.return_value.send_batch_message = Mock(return_value=mock_response)

    lambda_function.lambda_handler({}, {})

    assert mock_batch_processor.next_batch.call_count == 2

    mock_communication_management.assert_called_once()
    mock_communication_management.return_value.send_batch_message.assert_called_once_with(
        batch_id_1,
        routing_plan_id_1,
        recipients
    )
    mock_batch_processor.mark_batch_as_sent.assert_called_once_with(batch_id_1)
