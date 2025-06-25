import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate(
    lyric_emotions,
    emotion_audio_result,
    lyrics_text,
    model_name="gpt4o"
):
    """
    Generates 2 coherent prompts using either GPT-4o or Gemini (OpenAI-compatible API).

    Parameters:
        lyric_emotions (dict or str)
        emotion_audio_result (dict or str)
        lyrics_text (str)
        model_name (str): 'gpt4o' or 'gemini-1.5-flash'
        api_key (str or None): API key to use (will fallback to env var)

    Returns:
        list: Two parts of the storyboard (strings)
    """
    # Auto-load from env if not passed
    if model_name.lower() == "gemini-1.5-flash":
        api_key = os.getenv("GEMINI_API_KEY")
    elif model_name.lower() == "gpt4o":
        api_key = os.getenv("OPENAI_API_KEY")
    else:
        raise ValueError(f"❌ Unsupported model: {model_name}")

    if not api_key:
        raise ValueError("❌ API key must be provided or set in the .env file.")

    # Setup client
    if model_name.lower() == "gemini-1.5-flash":
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        is_openai = False
    else:
        import openai
        openai.api_key = api_key
        client = openai
        model_name = "gpt-4o"
        is_openai = True

    emotion_text = (
        lyric_emotions if isinstance(lyric_emotions, str)
        else lyric_emotions.get("label", "emotionally expressive")
    )

    prompt1 = (
        f"Generate a prompt for an 8-second cinematic video using the following inputs:\n\n"
        f"Lyrics: '{lyrics_text}'\n"
        f"Emotion from lyrics: '{emotion_text}'\n"
        f"Emotion from audio: '{emotion_audio_result}'\n\n"
        f"Make the prompt detailed and structure-aware — break it down by second or beat. "
        f"Include expressive visuals, cinematic camera movements, and dynamic actions of the main character, "
        f"who is a human-like capybara. Emphasize active scenes and forward narrative motion. "
        f"End the prompt with a clear note on tone and visual style (e.g., Pixar, 3D, painterly, etc.)."
    )

    try:
        response1 = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt1}],
            temperature=0.8
        )
        part1_text = response1.choices[0].message.content.strip()
    except Exception as e:
        return [f"❌ Error generating Part 1: {str(e)}"]

    prompt2 = (
        f"Continue the storyboard to create Part 2 (next 8 seconds) of a cinematic 16-second sequence.\n\n"
        f"--- PART 1 ---\n{part1_text}\n\n"
        f"Now write Part 2 using the same human-like capybara character, continuing the emotional tone of '{emotion_text}' "
        f"and the audio mood '{emotion_audio_result}'.\n\n"
        f"The lyrics playing are: '{lyrics_text}'.\n\n"
        f"Break the sequence into clear 2-second cinematic beats. Include dynamic character actions, expressive visuals, creative transitions, and impactful camera movements. "
        f"Maintain continuity with Part 1 while deepening the narrative emotion. End with a strong or surprising moment that makes viewers want to see more. "
        f"Keep the tone visually stylized and active. No dialogue or text overlays."
    )


    try:
        response2 = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt2}],
            temperature=0.8
        )
        part2_text = response2.choices[0].message.content.strip()
    except Exception as e:
        return [part1_text, f"❌ Error generating Part 2: {str(e)}"]

    return [part1_text, part2_text]
