import comms_management
import requests_mock


def test_get_read_messages(monkeypatch):
    monkeypatch.setenv("COMMGT_BASE_URL", "http://example.com")

    with requests_mock.Mocker() as rm:
        adapter = rm.get(
            "http://example.com/statuses",
            status_code=201,
            json={
                'status': 'success',
                'response': 'message_batch_post_response',
                'data': [{
                    'channel': 'nhsapp',
                    'channelStatus': 'delivered',
                    'supplierStatus': 'read',
                    'message_id': '2WL3qFTEFM0qMY8xjRbt1LIKCzM',
                    'message_reference': '1642109b-69eb-447f-8f97-ab70a74f5db4'
                }]
            }
        )

        response_json = comms_management.get_read_messages("c3b8e0c4-5f3d-4a2b-8c7f-1a2e9d6f3b5c")

        assert response_json["status"] == "success"
        assert len(response_json["data"]) == 1
        assert response_json["data"][0]["channel"] == "nhsapp"
        assert response_json["data"][0]["channelStatus"] == "delivered"
        assert response_json["data"][0]["supplierStatus"] == "read"
        assert response_json["data"][0]["message_id"] == "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
        assert response_json["data"][0]["message_reference"] == "1642109b-69eb-447f-8f97-ab70a74f5db4"

        assert adapter.called
        assert adapter.call_count == 1
        assert adapter.last_request.qs == {
            "batchreference": ["c3b8e0c4-5f3d-4a2b-8c7f-1a2e9d6f3b5c"],
            "channel": ["nhsapp"],
            "supplierstatus": ["read"],
        }


def test_get_read_messages_no_data(monkeypatch):
    monkeypatch.setenv("COMMGT_BASE_URL", "http://example.com")

    with requests_mock.Mocker() as rm:
        rm.get(
            "http://example.com/statuses",
            status_code=201,
            json={
                'status': 'success',
                'data': []
            }
        )

        response_json = comms_management.get_read_messages("c3b8e0c4-5f3d-4a2b-8c7f-1a2e9d6f3b5c")

        assert response_json["status"] == "success"
        assert response_json["data"] == []


def test_get_read_messages_exception(monkeypatch):
    monkeypatch.setenv("COMMGT_BASE_URL", "http://example.com")

    with requests_mock.Mocker() as rm:
        rm.get(
            "http://example.com/statuses",
            status_code=500,
            json={
                'status': 'error',
                'data': []
            }
        )

        response_json = comms_management.get_read_messages("c3b8e0c4-5f3d-4a2b-8c7f-1a2e9d6f3b5c")

        assert response_json["status"] == "error"
        assert response_json["data"] == []
