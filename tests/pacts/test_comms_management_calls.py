import os
import unittest
import requests
import pytest
from pact import Consumer, Provider
from pact.matchers import get_generated_values

def create_post_req(uri, message):
    return requests.post(uri, headers=headers(), json=message).json()

def headers():
    return notifier.headers("an_access_token", "e3e3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b")

@pytest.fixture
def create_message_pact():
    pact = Consumer("BatchNotificationProcessor").has_pact_with(
        Provider("CommsManagement"),
        pact_dir="tests/pacts",
    )
    pact.start_service()
    yield pact
    pact.stop_service()

def test_post_batch_message(create_message_pact):
    create_message_pact.given("A message is created")
    .upon_receiving("A request to send a batch message")
    .with_request("post", f"{os.getenv('COMMGT_BASE_URL')}/api/statuses", headers=headers(), body=message_body())
    .will_respond_with(201, body=expected_post_message_response())

    with create_message_pact:
        response = create_message_client(f"{os.getenv('COMMGT_BASE_URL')}/api/statuses", message_body())

    assert response == get_generated_values(expected_post_message_response())

def test_get_read_messages(self):
    self.assertEqual(True, False)  # add assertion here

