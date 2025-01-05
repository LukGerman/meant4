from io import BytesIO

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app, websocket_manager


@pytest.fixture
def test_client():
    return TestClient(app)


def test_base_route(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_image(test_client: TestClient):
    image_data = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded_image = cv2.imencode(".jpg", image_data)
    image_bytes = encoded_image.tobytes()

    mock_file = ("test.jpg", BytesIO(image_bytes), "image/jpeg")

    with test_client.websocket_connect("/faces") as websocket:
        response = test_client.post("/image", files={"image": mock_file})

        assert response.status_code == 200
        assert "image_url" in response.json()

        ws_data = websocket.receive_text()
        image_id = ws_data.split("/")[-1]

    response = test_client.get(f"/image/{image_id}")

    assert response.status_code == 200

    # Decode the output image from response content
    output_image = cv2.imdecode(
        np.frombuffer(response.content, np.uint8), cv2.IMREAD_UNCHANGED
    )

    # Compare the input and output images
    assert output_image.shape == image_data.shape
    assert np.array_equal(output_image, image_data)


def test_create_image_invalid_data(test_client: TestClient):
    mock_file = ("test.jpg", BytesIO(b"invalid data"), "image/jpeg")

    response = test_client.post("/image", files={"image": mock_file})

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid image data."


def test_create_image_invalid_format(test_client: TestClient):
    mock_file = ("test.txt", BytesIO(b"data"), "text/plain")

    response = test_client.post("/image", files={"image": mock_file})

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "Invalid file format. Only JPEG and PNG are supported."
    )


def test_websocket_endpoint(test_client: TestClient):
    # Connect to the WebSocket endpoint
    with test_client.websocket_connect("/faces") as websocket:
        # Assert the connection was added to active_connections
        assert len(websocket_manager.active_connections) == 1
        tracked_websocket = websocket_manager.active_connections[0]
        if tracked_websocket.client is not None:
            tracked_host, tracked_port = tracked_websocket.client
        else:
            pytest.fail("WebSocket client information is not available.")
        testclient_host, testclient_port = websocket.scope["client"]
        assert tracked_host == testclient_host
        assert tracked_port == testclient_port

        # Send a test message to ensure no errors occur
        websocket.send_text("Test Message")

    # After disconnecting, ensure the connection was removed
    assert len(websocket_manager.active_connections) == 0
