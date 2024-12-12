from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import os

def add_audio_every_10_seconds(video_path, audio_path, output_path):
    # Load the video and audio files
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Get the total duration of the video in seconds
    video_duration = video.duration  # in seconds

    # Initialize a list to store the video segments
    video_segments = []

    # Process the video in 10-minute chunks
    for start_time in range(0, int(video_duration), 10):  # 10 seconds = 10 minutes
        end_time = start_time + 10
        if end_time > video_duration:
            end_time = video_duration

        # Extract the video segment
        segment = video.subclipped(start_time, end_time)

        # If we are after the first 10 minutes, add the audio
        if start_time >= 10:
            # Set audio to play for 1 second at the start of this segment
            segment = segment.with_audio(audio.subclipped(0, 1))

        # Append the video segment
        video_segments.append(segment)

    # Concatenate all video segments into one
    final_video = concatenate_videoclips(video_segments)

    # Write the result to a file
    final_video.write_videofile(output_path, codec="libx264")
    
    if os.path.exists(output_path):
        return True
    else:
        False

        
# Example usage
# add_audio_every_10_minutes("video.mp4", "extended_audio.mp3", "output_video.mp4")
