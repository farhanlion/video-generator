from gradio_client import Client, handle_file
import re

def predict(audio_path, threshold=0.5):
    client = Client("amaai-lab/music2emo")
    result_text = client.predict(
        audio_path=handle_file(audio_path),
        threshold=threshold,
        api_name="/analyze_emotions"
    )[0]

    # Parse mood tags
    mood_line = re.search(r"Predicted Mood Tags: (.+?)💖", result_text, re.DOTALL)
    mood_tags = []
    if mood_line:
        tags_str = mood_line.group(1).strip().rstrip(',')  # remove ending comma
        tag_matches = re.findall(r"([\w\- ]+)\s*\(([\d.]+)\)", tags_str)
        mood_tags = [(tag.strip(), float(score)) for tag, score in tag_matches]

    # Parse valence and arousal
    valence_match = re.search(r"Valence:\s*([\d.]+)", result_text)
    arousal_match = re.search(r"Arousal:\s*([\d.]+)", result_text)

    valence = float(valence_match.group(1)) if valence_match else None
    arousal = float(arousal_match.group(1)) if arousal_match else None

    return {
        "tags": mood_tags,               # e.g. [('christmas', 0.97), ('holiday', 0.94), ...]
        "valence": valence,              # e.g. 4.05
        "arousal": arousal,              # e.g. 2.79
        "raw_text": result_text.strip()  # original string (optional)
    }
