from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest
import numpy as np

from app.settings import YunetSettings
from app.face_detector import FaceDetector
from app.main import get_image_path_by_id


@pytest.fixture
def yunet_settings():
    return YunetSettings(
        model_path="mock_model_path",
        input_size=(320, 320),
        score_threshold=0.5,
        nms_threshold=0.4,
        top_k=500,
    )


@pytest.fixture
def path_builder():
    return get_image_path_by_id()


@pytest.fixture
def face_detector(yunet_settings, path_builder):
    with patch("cv2.FaceDetectorYN.create") as mock_create:
        mock_model = MagicMock()
        mock_create.return_value = mock_model
        return FaceDetector(yunet_settings, path_builder)


@pytest.fixture
def mock_image():
    return np.zeros((320, 320, 3), dtype=np.uint8)


def test_detect_calls_model_methods(face_detector, path_builder, mock_image):
    """
    Tests the detect method of the FaceDetector class.

    """
    # Dummy image
    mock_faces = np.array(
        [
            [50, 50, 100, 100, 0.95],
            [150, 150, 80, 80, 0.85],
        ]
    )
    face_detector.model.detect.return_value = (None, mock_faces)
    image_id = uuid4()

    with patch("cv2.rectangle") as mock_rectangle, patch("cv2.imwrite") as mock_imwrite:
        face_detector.detect(mock_image, image_id)

        # Ensure model methods are called
        face_detector.model.setInputSize.assert_called_once_with((320, 320))
        face_detector.model.detect.assert_called_once_with(mock_image)

        # Ensure visualization (drawing rectangles) is called
        assert mock_rectangle.call_count == len(mock_faces)

        # Ensure the image is saved
        mock_imwrite.assert_called_once_with(path_builder(image_id), mock_image)


def test_visualize_no_faces(face_detector, mock_image):
    with patch("cv2.rectangle") as mock_rectangle:
        face_detector._visualize(mock_image, None)
        mock_rectangle.assert_not_called()


def test_visualize_with_faces(face_detector, mock_image):
    mock_faces = np.array(
        [
            [50, 50, 100, 100, 0.95],
            [150, 150, 80, 80, 0.85],
        ]
    )

    with patch("cv2.rectangle") as mock_rectangle:
        face_detector._visualize(mock_image, mock_faces)

        # Ensure rectangles are drawn for each face
        assert mock_rectangle.call_count == len(mock_faces)
        mock_rectangle.assert_any_call(
            img=mock_image,
            pt1=(50, 50),
            pt2=(150, 150),
            color=(0, 255, 0),
            thickness=2,
        )
        mock_rectangle.assert_any_call(
            img=mock_image,
            pt1=(150, 150),
            pt2=(230, 230),
            color=(0, 255, 0),
            thickness=2,
        )
