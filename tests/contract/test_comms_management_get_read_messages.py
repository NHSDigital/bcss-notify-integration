from pact import Consumer, Provider, Term
from pact.matchers import get_generated_values
import pytest
from comms_management import get_read_messages

@pytest.fixture
def get_statuses_pact():
  pact = Consumer("MessageStatusHandler").has_pact_with(
      Provider("CommunicationManagement"),
      pact_dir="tests/contract/pacts",
  )
  pact.start_service()
  yield pact
  pact.stop_service()

def test_get_read_messages(get_statuses_pact, monkeypatch):
    monkeypatch.setenv("COMMGT_BASE_URL", get_statuses_pact.uri)
    monkeypatch.setenv("API_KEY","test_api_key")

    expected_response = {
                'status': 'success',
                'response': 'message_batch_post_response',
                'data': [{
                    'channel': 'nhsapp',
                    'channelStatus': 'delivered',
                    'supplierStatus': 'read',
                    "id": Term(r"[0-9a-zA-Z\-]{27}", "2HL3qFTEFM0qMY8xjRbt1LIKCzM"),
                    'message_reference': '1642109b-69eb-447f-8f97-ab70a74f5db4',
                    "messageReference": Term(r"[0-9a-zA-Z\-]{36}", "da0b1495-c7cb-468c-9d81-07dee089d728"),
                }]
            }

    endpoint = "/api/statuses"
    uri = get_statuses_pact.uri + endpoint

    (get_statuses_pact.given("There are read messages")
     .upon_receiving("A request to get read messages")
     .with_request("GET", "/api/statuses")
     .will_respond_with(201, body=expected_response))

    with get_statuses_pact:
        response = get_read_messages('123456')

        assert response == get_generated_values(expected_response)
