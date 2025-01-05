from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class YunetSettings(BaseModel):
    # Path to .onnx model file
    model_path: str
    # Shape of input file
    input_size: tuple[int, int] = (320, 320)
    # Threshold for filtering out faces with conf < conf_thresh
    score_threshold: float = 0.6
    # Threshold for non-max suppression
    nms_threshold: float = 0.3
    # Keep keep_top_k for results outputing
    top_k: int = 5000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    app_name: str = "Meant4 Face Detector"
    # Yunet model settings
    yunet_settings: YunetSettings
    # Base directory for output files
    output_dir: Path = Path("detected")
