# 🎵 Emotion-Aware Music Video Generator

This is a Flask-based web application that automatically generates cinematic music videos from audio input using AI-driven transcription, emotion detection, and video generation.

---

## 🌟 Features

- 🎧 Upload a song (MP3/WAV)
- 📝 Transcribe lyrics using OpenAI Whisper
- 🎵 Extract the chorus using `pychorus` (built on Librosa)
- 🎭 Detect emotions from both audio and lyrics
- ✨ Generate detailed video prompts using GPT-4o or Gemini 1.5 Flash
- 🎥 Create cinematic scenes using Google's Veo (8s × 2)
- 🎬 Stitch clips + audio using MoviePy
- 🔗 Watch or download the final video directly from your browser

---

## 🧠 AI & Tools Used

| Tool / API              | Purpose                                         |
|-------------------------|-------------------------------------------------|
| OpenAI Whisper API      | Transcribe lyrics from audio                    |
| pychorus + Librosa      | Detect and extract chorus                       |
| Hugging Face (custom)   | Detect emotion from lyrics                      |
| music2emotion API       | Detect emotion from audio                       |
| GPT-4o / Gemini 1.5 API | Generate cinematic video prompts                |
| Google Veo 2.0          | Generate video scenes from prompts              |
| MoviePy                 | Stitch video clips and overlay audio            |
| Flask                   | Web backend                                     |
| HTML5 + CSS + JavaScript| Frontend interface                              |

---

## 📦 Folder Structure

```
├── app.py # Flask backend entry point
├── templates/ # HTML templates
├── static/
│   ├── uploads/ # Uploaded and processed files
│   ├── videos/ # Generated video outputs
│   └── style/ # CSS and static assets
├── utils/
│   ├── transcribe.py # Whisper transcription logic
│   ├── emotion_audio.py # Audio emotion detection
│   ├── emotion_lyrics.py # Lyrics emotion classification
│   ├── postprocess.py # Stitching videos and audio
│   ├── chorus.py # Chorus extraction using pychorus
│   ├── prompt_gen.py # Prompt creation using GPT or Gemini
│   └── video_gen.py # Google Veo video generation
├── requirements.txt # Python package dependencies
├── .env # API keys and secrets
└── README.md # This file
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/emotion-music-generator.git
cd emotion-music-generator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Environment Variables

Create a `.env` file in the root directory and add:

```env
OPENAI_API_KEY=your_open_ai_key
GOOGLE_CLOUD_PROJECT=your_gcp_project
GOOGLE_STORAGE_BUCKET=gs://your-storage-bucket
```

### 4. Run the App

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🧪 Sample Use Case

1. User uploads a song (e.g., `enchanted.mp3`)
2. App transcribes lyrics and extracts chorus
3. Emotion is detected from both audio and lyrics
4. Prompts are generated and fed to Google Veo to create two 8s clips
5. Final video is stitched with chorus audio and displayed to the user

---

## 📌 Notes

- Output video is fixed to 16 seconds (two 8s clips).
- The generated character in the video is a stylized human-like capybara 🐾.
- This is an academic/experimental prototype and depends on API access to OpenAI, Google Veo, and Hugging Face models.
