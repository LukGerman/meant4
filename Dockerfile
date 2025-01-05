ARG MODEL_NAME=face_detection_yunet_2023mar.onnx
ARG MODEL_PATH=https://github.com/opencv/opencv_zoo/raw/a988f337936a624cb62fd58958116ba8b0a98afa/models/face_detection_yunet/face_detection_yunet_2023mar.onnx?download=

FROM python:3.13-bookworm AS builder

ARG MODEL_NAME
ARG MODEL_PATH

ARG POETRY_NO_INTERACTION=1
ARG POETRY_VIRTUALENVS_IN_PROJECT=1
ARG POETRY_VIRTUALENVS_CREATE=1
ARG POETRY_CACHE_DIR=/tmp/poetry_cache

RUN wget -O $MODEL_NAME $MODEL_PATH

RUN pip install poetry==1.8.5

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.13-slim-bookworm AS runtime

ARG MODEL_NAME

# Copy face detection model
ENV YUNET_SETTINGS__MODEL_PATH=./app/${MODEL_NAME}
COPY --from=builder ${MODEL_NAME} ${YUNET_SETTINGS__MODEL_PATH} 

# Copy virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY app ./app

EXPOSE 8282

CMD ["fastapi", "run", "app/main.py", "--port", "8282"]
