from pact import Consumer, Provider, Term
from pact.matchers import get_generated_values
import pytest
from communication_management import CommunicationManagement
from recipient import Recipient

@pytest.fixture
def send_batch_pact():
  pact = Consumer("MessageStatusHandler").has_pact_with(
      Provider("CommunicationManagement"),
      pact_dir="tests/contract/pacts",
  )
  pact.start_service()
  yield pact
  pact.stop_service()

def test_send_batch_message(send_batch_pact, monkeypatch):
    comms_management = CommunicationManagement()
    comms_management.base_url = send_batch_pact.uri
    comms_management.api_key = "test_api_key"

    expected_reponse = {
                "data": {
                    "type": "MessageBatch",
                    "attributes": {
                        "routingPlanId": Term(r"[0-9a-zA-Z\-]{27}", "2HL3qFTEFM0qMY8xjRbt1LIKCzM"),
                        "messageReference": Term(r"[0-9a-zA-Z\-]{36}", "da0b1495-c7cb-468c-9d81-07dee089d728"),
                        "messages": [
                            {
                                "recipient": {"nhsNumber": "0000000000"},
                                "messageReference": "message_reference_0",
                                "personalisation": {},
                            },
                            {
                                "recipient": {"nhsNumber": "1111111111"},
                                "messageReference": "message_reference_1",
                                "personalisation": {},
                            },
                        ],
                    },
                },
            }

    endpoint = "/message/batch"
    uri = send_batch_pact.uri + endpoint

    (send_batch_pact.given("There are messages to send")
        .upon_receiving("A request to send a batch message")
        .with_request("POST", "/message/batch")
        .will_respond_with(201, body=expected_reponse))

    with send_batch_pact:
        response = comms_management.send_batch_message(
            batch_id="123456789",
            routing_config_id="987654321",
            recipients=[
                Recipient(("0000000000", "message_reference_0", "requested")),
                Recipient(("1111111111", "message_reference_1", "requested")),
            ]
        ).json()

        assert response == get_generated_values(expected_reponse)