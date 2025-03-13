from communication_management import CommunicationManagement
from recipient import Recipient
import pytest
import requests_mock
import unittest.mock


class TestCommunicationManagement:
    @pytest.fixture
    def setup(self, monkeypatch):
        monkeypatch.setenv("base_url", "http://example.com")
        monkeypatch.setenv("application_id", "application_id")
        monkeypatch.setenv("api_key", "api_key")


    def test_send_batch_message(self, setup):
        subject = CommunicationManagement()

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                "http://example.com/api/message/batch",
                status_code=201,
                json={"data": {"id": "batch_id"}},
            )

            subject.send_batch_message(
                "batch_id",
                "routing_config_id",
                [
                    ["0000000000", "message_reference_0"],
                    ["1111111111", "message_reference_1"],
                ]
            )
            assert adapter.last_request.url == "http://example.com/api/message/batch"
            assert adapter.last_request.headers["x-api-key"] == "api_key"
            assert adapter.last_request.json() == {
                "data": {
                    "type": "MessageBatch",
                    "attributes": {
                        "routingPlanId": "routing_config_id",
                        "messageBatchReference": "batch_id",
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

    def test_generate_batch_message_request_body(self, setup):
        recipients_data = [
            ["0000000000", "message_reference_0"],
            ["1111111111", "message_reference_1"],
        ]

        subject = CommunicationManagement()

        message_batch = subject.generate_batch_message_request_body("routing_config_id", "batch_reference", recipients_data)

        assert message_batch["data"]["attributes"]["routingPlanId"] == "routing_config_id"
        assert message_batch["data"]["attributes"]["messageBatchReference"] == "batch_reference"
        assert len(message_batch["data"]["attributes"]["messages"]) == 2
        assert message_batch["data"]["attributes"]["messages"][0]["recipient"]["nhsNumber"] == "0000000000"
        assert message_batch["data"]["attributes"]["messages"][0]["messageReference"] == "message_reference_0"
        assert message_batch["data"]["attributes"]["messages"][1]["recipient"]["nhsNumber"] == "1111111111"
        assert message_batch["data"]["attributes"]["messages"][1]["messageReference"] == "message_reference_1"


    def test_generate_message(self, setup):
        recipient_data = ["0000000000", "message_reference_0"]

        subject = CommunicationManagement()

        message = subject.generate_message(recipient_data)

        assert message["messageReference"] == "message_reference_0"
        assert message["recipient"]["nhsNumber"] == "0000000000"
        assert message["personalisation"] == {}
