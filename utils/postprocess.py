import os
import moviepy.editor as mp


def stitch(video_path: str, audio_path: str, output_folder: str = "static/videos") -> str:
    """
    Combines a single video with the chorus audio and exports the final video.

    Args:
        video_path (str): Path to downloaded video file
        audio_path (str): Path to extracted chorus audio file
        output_folder (str): Folder to save the stitched video

    Returns:
        str: Path to the final stitched video
    """
    try:
        video_clip = mp.VideoFileClip(video_path)
        audio_clip = mp.AudioFileClip(audio_path)

        # Trim audio if it's longer than the video
        if audio_clip.duration > video_clip.duration:
            audio_clip = audio_clip.subclip(0, video_clip.duration)

        final_video = video_clip.set_audio(audio_clip)

        os.makedirs(output_folder, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(output_folder, f"{base_name}_stitched.mp4")

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )

        video_clip.close()
        audio_clip.close()
        final_video.close()

        return output_path

    except Exception as e:
        print(f"❌ Error during single video stitching: {e}")
        return ""


def stitch_multiple(video_paths: list, audio_path: str, output_folder: str = "static/videos") -> str:
    """
    Concatenates multiple videos and overlays chorus audio on the final stitched video.

    Args:
        video_paths (list): List of video file paths
        audio_path (str): Path to chorus audio file
        output_folder (str): Folder to save the final video

    Returns:
        str: Path to the final stitched video
    """
    try:
        # Load and optionally resize videos (uncomment to speed up further)
        video_clips = [mp.VideoFileClip(p) for p in video_paths]
        # video_clips = [mp.VideoFileClip(p).resize(height=720) for p in video_paths]

        concatenated = mp.concatenate_videoclips(video_clips, method="compose")

        audio_clip = mp.AudioFileClip(audio_path)

        # Trim audio if it's longer than the stitched video
        if audio_clip.duration > concatenated.duration:
            audio_clip = audio_clip.subclip(0, concatenated.duration)

        final_video = concatenated.set_audio(audio_clip)

        os.makedirs(output_folder, exist_ok=True)
        base_name = "_".join([os.path.splitext(os.path.basename(p))[0] for p in video_paths])
        output_path = os.path.join(output_folder, f"{base_name}_stitched.mp4")

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )

        # Cleanup
        for clip in video_clips:
            clip.close()
        audio_clip.close()
        final_video.close()

        return output_path

    except Exception as e:
        print(f"❌ Error during multiple video stitching: {e}")
        return ""
