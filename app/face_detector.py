from typing import Callable
from uuid import UUID

import numpy as np
import cv2 as cv

from app.settings import YunetSettings


class FaceDetector:
    def __init__(
        self, yunet_settings: YunetSettings, image_path_resolver: Callable[[UUID], str]
    ) -> None:
        self.model = cv.FaceDetectorYN.create(
            model=yunet_settings.model_path,
            config="",
            input_size=yunet_settings.input_size,
            score_threshold=yunet_settings.score_threshold,
            nms_threshold=yunet_settings.nms_threshold,
            top_k=yunet_settings.top_k,
        )
        self.image_path_resolver = image_path_resolver

    def detect(self, image: cv.typing.MatLike, image_id: UUID) -> None:
        self.model.setInputSize((image.shape[1], image.shape[0]))
        _, faces = self.model.detect(image)

        self._visualize(image, faces)

        cv.imwrite(self.image_path_resolver(image_id), image)

    def _visualize(self, image: cv.typing.MatLike, faces: np.ndarray | None) -> None:
        if faces is None:
            return

        for face in faces:
            coords = face[:-1].astype(np.int32)
            # Draw face bounding box
            cv.rectangle(
                img=image,
                pt1=(coords[0], coords[1]),
                pt2=(coords[0] + coords[2], coords[1] + coords[3]),
                color=(0, 255, 0),
                thickness=2,
            )
