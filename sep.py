from moviepy.video.io.VideoFileClip import VideoFileClip

def separate_audio_video(video_path, audio_output_path, video_output_path):
    video = VideoFileClip(video_path)
    
    # Extract audio
    audio = video.audio
    audio.write_audiofile(audio_output_path)

    # Get video without audio
    video_without_audio = video.without_audio()
    video_without_audio.write_videofile(video_output_path, codec='libx264')

# Usage
separate_audio_video("input.mp4", "output_audio.mp3", "output_video.mp4")