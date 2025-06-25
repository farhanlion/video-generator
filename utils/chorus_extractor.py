from pychorus.helpers import find_and_output_chorus
import os

def extract(audio_path, output_dir='static/uploads'):
    """
    Extracts the chorus section from an audio file.

    Args:
        audio_path (str): Path to the input audio file (e.g., .mp3).
        output_dir (str): Directory to save the chorus clip.

    Returns:
        tuple: (output_chorus_path, (start_time, end_time))
    """
    # Output path for chorus clip
    output_chorus_path = os.path.join(
        output_dir,
        f"chorus_clip_{os.path.basename(audio_path).split('.')[0]}.wav"
    )

    # Extract 30-second chorus
    chorus_start_time = find_and_output_chorus(
        input_file=audio_path,
        output_file=output_chorus_path,
        clip_length=16
    )

    chorus_end_time = chorus_start_time + 8  # Assuming fixed length
    return output_chorus_path, (chorus_start_time, chorus_end_time)
