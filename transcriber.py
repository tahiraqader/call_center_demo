import soundfile as sf
import numpy as np
from transformers import pipeline
def split_audio(audio, sample_rate, chunk_duration_s=300):
    """
    Split audio into smaller chunks of specified duration (in seconds).
    """
    chunk_size = int(sample_rate * chunk_duration_s)
    chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]
    return chunks

def create_dialog_format(left_transcription, right_transcription):
    """
    Create a dialog format by alternating between the two transcriptions.
    """
    # Split each transcription by sentences or time-based chunks
    left_lines = left_transcription.split('. ')
    right_lines = right_transcription.split('. ')

    # Alternate between the two speakers (left: caller, right: agent)
    dialog = []
    for left_line, right_line in zip(left_lines, right_lines):
        dialog.append(f"Caller: {left_line}")
        dialog.append(f"Agent: {right_line}")

    return "\n".join(dialog)


def load_and_split_audio(file_path):
    """
    Load stereo audio and split it into left and right channels (mono).
    """
    audio, sample_rate = sf.read(file_path)

    if audio.ndim == 2:  # Stereo file
        left_channel = audio[:, 0]  # Left channel (caller)
        right_channel = audio[:, 1]  # Right channel (agent)
    else:  # Mono file
        left_channel = audio
        right_channel = audio

    return left_channel, right_channel, sample_rate

def transcribe_channel(channel_audio, sample_rate, model_name="openai/whisper-medium"):
    """
    Transcribe a single mono channel using Whisper ASR model from Hugging Face.
    """
    # Initialize the pipeline for transcription
    asr_pipeline = pipeline("automatic-speech-recognition", model=model_name, chunk_length_s=30)

    # Convert audio to the format that the model expects
    audio_input = {"array": channel_audio, "sampling_rate": sample_rate}

    # Transcribe the audio
    transcription = asr_pipeline(audio_input)
    return transcription["text"]
def process_audio_file(file_path, chunk_duration_s=300):
    """
    Process the stereo audio file, split into mono channels, transcribe, and diarize.
    """
    # Step 1: Load and split audio into left and right channels
    left_channel, right_channel, sample_rate = load_and_split_audio(file_path)

    # Step 2: Split audio if it's too long (e.g., greater than 5 minutes)
    if len(left_channel) > sample_rate * chunk_duration_s:
        left_chunks = split_audio(left_channel, sample_rate, chunk_duration_s)
        right_chunks = split_audio(right_channel, sample_rate, chunk_duration_s)
    else:
        left_chunks = [left_channel]
        right_chunks = [right_channel]

    # Step 3: Transcribe each chunk
    dialog_segments = []
    for left_chunk, right_chunk in zip(left_chunks, right_chunks):
        left_transcription = transcribe_channel(left_chunk, sample_rate)
        right_transcription = transcribe_channel(right_chunk, sample_rate)
        
        # Step 4: Combine into dialog format
        dialog_segment = create_dialog_format(left_transcription, right_transcription)
        dialog_segments.append(dialog_segment)

    # Step 5: Combine all dialog segments
    final_dialog = "\n".join(dialog_segments)
    return final_dialog

# Example usage:
file_path = "mock_fraud_2.wav"
dialog = process_audio_file(file_path)
print(dialog)

