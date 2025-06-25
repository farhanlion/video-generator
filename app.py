from flask import Flask, jsonify, request, render_template, send_file
from threading import Thread
import os
import time
from dotenv import load_dotenv
from google.cloud import storage

from utils import (
    transcribe,
    chorus_extractor,
    emotion_audio,
    emotion_lyrics,
    prompt_gen,
    video_gen,
    postprocess,
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PROCESS_STATUS = {
    "message": "Waiting to start…",
    "done": False,
    "video_path": "",
    "data": {},
    "status_updates": []
}

@app.route("/")
def index():
    return render_template("index.html")

def process_audio(audio_path: str, model_name: str):
    global PROCESS_STATUS
    PROCESS_STATUS.update({
        "message": "Starting…",
        "done": False,
        "video_path": "",
        "data": {},
        "status_updates": []
    })

    PROCESS_STATUS["status_updates"].append(f"🤖 Using model: {model_name}")

    # 🔤 Transcription
    PROCESS_STATUS["message"] = "🔤 Transcribing audio…"
    lyrics = transcribe.run_whisper(audio_path)
    PROCESS_STATUS["data"]["lyrics"] = lyrics
    PROCESS_STATUS["status_updates"].append(f"🔤 Transcribed {len(lyrics.split())} words.")

    # 🎼 Chorus extraction
    PROCESS_STATUS["message"] = "🎼 Extracting chorus…"
    chorus_clip_path, chorus_times = chorus_extractor.extract(audio_path)
    PROCESS_STATUS["data"]["chorus_audio_url"] = f"/static/uploads/{os.path.basename(chorus_clip_path)}"
    PROCESS_STATUS["status_updates"].append(f"🎼 Chorus: {chorus_times[0]:.2f}s–{chorus_times[1]:.2f}s")

    # 🎧 Audio emotion
    PROCESS_STATUS["message"] = "🎧 Detecting emotions from audio…"
    emotion_audio_result = emotion_audio.predict(chorus_clip_path)
    PROCESS_STATUS["data"]["audio_emotions"] = emotion_audio_result
    PROCESS_STATUS["status_updates"].append("🎧 Audio emotion OK")

    # 🧠 Lyric emotion
    PROCESS_STATUS["message"] = "🧠 Detecting emotions from lyrics…"
    emotion_text = emotion_lyrics.detect(lyrics)
    PROCESS_STATUS["data"]["lyric_emotions"] = emotion_text
    PROCESS_STATUS["status_updates"].append(
        f"🧠 Lyric emotion = {emotion_text['label']} ({emotion_text['confidence']*100:.1f}%)"
    )

    # 🎬 Prompt generation
    PROCESS_STATUS["message"] = "🎬 Generating visual prompts…"
    prompts = prompt_gen.generate(
        lyric_emotions=emotion_text,
        emotion_audio_result=emotion_audio_result,
        lyrics_text=lyrics,
        model_name=model_name
    )
    PROCESS_STATUS["data"]["prompts"] = prompts
    PROCESS_STATUS["status_updates"].append(f"🎬 Generated {len(prompts)} prompts")

    video_paths = []

    for i, prompt in enumerate(prompts):
        PROCESS_STATUS["message"] = f"📽️ Generating video {i+1} of {len(prompts)}…"
        video_gen_result = video_gen.generate_video(prompt)

        if video_gen_result["status"] != "success":
            PROCESS_STATUS["status_updates"].append(f"❌ Video {i+1} generation failed: {video_gen_result['error']}")
            PROCESS_STATUS.update({"message": "❌ Video generation failed", "done": True})
            return

        video_url = video_gen_result["uri"]
        PROCESS_STATUS["status_updates"].append(f"📽️ Video {i+1} ready (job {video_gen_result['operation_id']})")

        video_filename = os.path.basename(video_url)
        video_output_path = os.path.join("static/videos", f"{i}_{video_filename}")

        if video_url.startswith("gs://"):
            bucket_name, blob_path = video_url[5:].split("/", 1)
            storage_client = storage.Client()
            blob = storage_client.bucket(bucket_name).blob(blob_path)

            try:
                blob.download_to_filename(video_output_path)
                PROCESS_STATUS["status_updates"].append(f"📥 Downloaded video {i+1} to {video_output_path}")
                video_paths.append(video_output_path)
            except Exception as e:
                PROCESS_STATUS["status_updates"].append(f"❌ GCS download failed for video {i+1}: {e}")
                PROCESS_STATUS.update({"message": "❌ Failed to download video", "done": True})
                return
        else:
            PROCESS_STATUS["status_updates"].append(f"❌ Invalid URI for video {i+1}")
            PROCESS_STATUS.update({"message": "❌ Invalid video URL", "done": True})
            return

    # 🧵 Stitching videos
    PROCESS_STATUS["message"] = "🧵 Stitching final video…"
    stitched_folder = os.path.join("static", "processed_videos")
    os.makedirs(stitched_folder, exist_ok=True)

    final_video_path = postprocess.stitch_multiple(
        video_paths,
        chorus_clip_path,
        output_folder=stitched_folder
    )

    PROCESS_STATUS["video_path"] = f"/download?path={final_video_path}"
    PROCESS_STATUS["status_updates"].append("🧵 Final stitched video ready")

    PROCESS_STATUS.update({
        "message": "✅ Done!",
        "done": True
    })

@app.route("/process", methods=["POST"])
def process():
    audio_file = request.files["audio"]
    model_name = request.form.get("model")  # from form input
    audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(audio_path)
    Thread(target=process_audio, args=(audio_path, model_name)).start()
    return "", 202

@app.route("/status")
def status():
    return jsonify(PROCESS_STATUS)

@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
