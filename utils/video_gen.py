# video_gen.py

import time
import os
from google import genai
from google.genai.types import GenerateVideosConfig
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
    http_options=types.HttpOptions(api_version='v1')
)

def generate_video(prompt: str, aspect_ratio: str = "16:9") -> dict:
    """Generate a video using the Veo model with the given prompt."""
    print(prompt)

    output_gcs_uri = os.getenv("GOOGLE_STORAGE_BUCKET")

    operation = client.models.generate_videos(
        model="veo-2.0-generate-001",
        # model="veo-3.0-generate-preview",
        prompt=prompt,
        config=GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            output_gcs_uri=output_gcs_uri
        ),
    )

    # Poll until done
    timeout = 600  # 10 minutes
    start = time.time()
    while not operation.done and time.time() - start < timeout:
        time.sleep(15)
        operation = client.operations.get(operation)

    if operation.response:
        return {
            "status": "success",
            "uri": operation.result.generated_videos[0].video.uri,
            "operation_id": operation.name
        }

    return {
        "status": "failed",
        "error": str(operation.error) if operation.error else "Unknown error"
    }
