from typing import Annotated, Callable
from uuid import UUID, uuid4

import cv2 as cv
import numpy as np

from fastapi import (
    BackgroundTasks,
    HTTPException,
    Request,
    UploadFile,
    Depends,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.face_detector import FaceDetector
from app.settings import Settings
from app.websockets import ConnectionManager


# Globals
settings = Settings()
websocket_manager = ConnectionManager()
templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create directory for output files
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    yield


# App init
app = FastAPI(lifespan=lifespan)


# Dependencies
def get_image_path_by_id() -> Callable[[UUID], str]:
    def func(image_id: UUID) -> str:
        """
        Helper funtion to get path to image by it's id

        """
        return str(settings.output_dir / f"{image_id}.jpg")

    return func


ImagePathResolverDep = Annotated[Callable[[UUID], str], Depends(get_image_path_by_id)]


def get_face_detector(image_path_resolver: ImagePathResolverDep) -> FaceDetector:
    return FaceDetector(settings.yunet_settings, image_path_resolver)


FaceDetectorDep = Annotated[FaceDetector, Depends(get_face_detector)]


# Routes
@app.get("/", response_class=HTMLResponse)
async def base(request: Request):
    return templates.TemplateResponse(
        request=request, name="base.html", context={"url": request.url}
    )


@app.get("/image/{image_id}", response_class=FileResponse)
async def retrieve_image(image_id: UUID, image_path_resolver: ImagePathResolverDep):
    return image_path_resolver(image_id)


@app.post("/image")
async def create_image(
    image: UploadFile,
    face_detector: FaceDetectorDep,
    background_tasks: BackgroundTasks,
    request: Request,
):
    # Ensure the file is an image
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid file format. Only JPEG and PNG are supported.",
        )

    contents = await image.read()
    cv_image = cv.imdecode(np.frombuffer(contents, np.uint8), cv.IMREAD_COLOR)

    # Ensure the image was successfully decoded
    if cv_image is None:
        raise HTTPException(status_code=422, detail="Invalid image data.")

    # Register background tasks and return response right away
    image_id = uuid4()
    image_url = f"{request.url}/{image_id}"
    background_tasks.add_task(face_detector.detect, cv_image, image_id)
    background_tasks.add_task(websocket_manager.broadcast, image_url)

    return {"image_url": image_url}


@app.websocket("/faces")
async def websocket_endpoint(
    websocket: WebSocket,
):
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
