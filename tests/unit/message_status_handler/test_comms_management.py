import unittest
import requests_mock

from comms_management import get_statuses

def test_get_statuses():
    with requests_mock.Mocker() as rm:
        rm.get(
            "http://example.com/statuses",
            status_code=201,
            json={'status': 'success',
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

        response = get_statuses('1234', '5678')
        response_json = response.json()

        assert response.status_code == 201
        assert response_json["status"] == "success"
        assert len(response_json["data"]) == 1
        assert response_json["data"][0]["channel"] == "nhsapp"
        assert response_json["data"][0]["channelStatus"] == "delivered"
        assert response_json["data"][0]["supplierStatus"] == "read"
        assert response_json["data"][0]["message_id"] == "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
        assert response_json["data"][0]["message_reference"] == "1642109b-69eb-447f-8f97-ab70a74f5db4"