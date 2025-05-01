
# --- Imports ---
import numpy as np
import soundfile as sf
import torch
from io import BytesIO
from faster_whisper import WhisperModel
from transformers import pipeline
import spacy



# --- Setup model ONCE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "small"   # Use "tiny" for even faster speeds
model = WhisperModel(model_size, device=device, compute_type="int8" if device == "cpu" else "float16")

# # Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

# # Define a Hugging Face summarization pipeline (optional step for summarizing the call transcript)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# --- Utility Functions ---

def split_stereo_audio(audio, sample_rate, max_duration_s=60, overlap_s=1):
    """
    Split stereo audio into chunks keeping channels synchronized.
    """
    samples_per_chunk = int(sample_rate * max_duration_s)
    samples_overlap = int(sample_rate * overlap_s)

    chunks = []
    start = 0
    while start < len(audio):
        end = min(start + samples_per_chunk, len(audio))
        chunk = audio[start:end, :]
        chunks.append(chunk)
        start += samples_per_chunk - samples_overlap
    return chunks

def transcribe_channel(audio_array, sample_rate):
    """
    Transcribe a single mono audio.
    """
    buffer = BytesIO()
    sf.write(buffer, audio_array, sample_rate, format="WAV")
    buffer.seek(0)
    
    segments, _ = model.transcribe(buffer)
    results = []
    for seg in segments:
        results.append((seg.start, seg.end, seg.text))
    return results

def process_chunk(chunk, sample_rate):
    """
    Process one stereo chunk: transcribe left and right channels separately and merge them.
    """
    caller_audio = chunk[:, 0]
    agent_audio = chunk[:, 1]

    # Transcribe channels independently
    caller_segs = transcribe_channel(caller_audio, sample_rate)
    agent_segs = transcribe_channel(agent_audio, sample_rate)

    merged_dialog = []
    i, j = 0, 0

    # Merge based on start time from both segments
    while i < len(caller_segs) or j < len(agent_segs):
        # Check if caller's segment starts before agent's
        if i < len(caller_segs) and (j >= len(agent_segs) or caller_segs[i][0] <= agent_segs[j][0]):
            merged_dialog.append(f"Caller: {caller_segs[i][2]}")
            i += 1
        # Otherwise, handle the agent's segment
        else:
            merged_dialog.append(f"Agent: {agent_segs[j][2]}")
            j += 1

    return merged_dialog

def transcribe_stereo_file_dialog(audio, sample_rate, max_duration_s=60, overlap_s=1):
    """
    Full pipeline: load stereo audio, split it, process it chunk by chunk.
    """
    # audio, sample_rate = sf.read(file_path)

    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("Audio must be stereo (2 channels)")

    stereo_chunks = split_stereo_audio(audio, sample_rate, max_duration_s, overlap_s)

    full_dialog = []
    for idx, chunk in enumerate(stereo_chunks):
        print(f"Processing chunk {idx+1}/{len(stereo_chunks)}...")
        chunk_dialog = process_chunk(chunk, sample_rate)
        full_dialog.extend(chunk_dialog)

    return full_dialog
# dialog = transcribe_stereo_file_dialog("mock_fraud_2.wav", max_duration_s=60, overlap_s=1)

# for line in dialog:
#     print(line)

##############################


def summarize_conversation1(dialog_list, max_chunk_chars=4000):
    """
    Summarizes a full conversation (agent and caller) carefully.

    Args:
        dialog_list: List of dialog lines like ["Agent: Hello", "Caller: I need help"]
        max_chunk_chars: Maximum character length per chunk (safe for model input limits)

    Returns:
        A full conversation summary as a string.
    """

    # Merge the conversation into one big text with "Agent:" and "Caller:" markers
    conversation_text = "\n".join(dialog_list)
    print('==================')
    print(conversation_text)

    # Huggingface models have input size limits, so split if needed
    inputs = []
    current_chunk = ""
    for line in conversation_text.split("\n"):
        if len(current_chunk) + len(line) < max_chunk_chars:
            current_chunk += line + "\n"
        else:
            inputs.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        inputs.append(current_chunk.strip())

    # Summarize each chunk
    summaries = []
    for idx, chunk in enumerate(inputs):
        print(f"Summarizing chunk {idx+1}/{len(inputs)}...")
        summary = summarizer(chunk, max_length=256, min_length=50, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    # Combine all chunk summaries
    final_summary = "\n".join(summaries)
    return final_summary
# summary = summarize_conversation(dialog)

# # Step 3: Output
# print("\n=== SUMMARY ===\n")
# print(summary)

# import spacy
# #TQ this works well
# from transformers import pipeline

# # Load spaCy's small English model
# nlp = spacy.load("en_core_web_sm")

# # Define a Hugging Face summarization pipeline (optional step for summarizing the call transcript)
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn",from_tf=True)



# # Define a list of action verbs commonly used in customer service dialogues
# action_verbs = [ "verify", "schedule", "send", "update", "confirm", "resolve", "remind"]

# # Function to identify action items in the transcript
# def extract_action_items_from_transcript(transcript_text):
#     """
#     Extracts action items from the transcript based on action verbs and their related entities.
#     """
#     doc = nlp(transcript_text)
    
#     # List to store extracted action items
#     action_items = []

#     # Loop through each sentence in the document
#     for sent in doc.sents:
#         # Find verbs in the sentence
#         verbs = [token for token in sent if token.pos_ == "VERB" and token.lemma_ in action_verbs]
        
#         # Check if there are any action verbs in the sentence
#         if verbs:
#             # Extract direct objects (things being acted upon)
#             action_objects = [token for token in sent if token.dep_ in ["dobj", "prep", "attr"]]
            
#             # Optionally extract entities (like dates, locations, account info) to filter action items
#             entities = [ent for ent in sent.ents]

#             # If the sentence contains action verbs and relevant objects or entities, it's an action item
#             if action_objects or entities:
#                 action_items.append(sent.text.strip())

#     return action_items

# # Example of a transcribed customer service call


# # Optional: Summarize the transcript before extracting actions (if the transcript is too long or detailed)
#summarized_transcript = summarizer(transcript)[0]['summary_text']

# # Extract action items from the transcript (summarized or full)
# action_items = extract_action_items_from_transcript(summary)

# # Display the extracted action items
# print("Extracted Action Items:")
# for item in action_items:
#     print(f"- {item}")
def process_call(audio, sample_rate):
    dialog = transcribe_stereo_file_dialog(audio, sample_rate)

    summary = summarize_conversation(dialog)
    action_items = extract_action_items_from_transcript(summary)
    data = {
        "dialog": dialog,
        "summary": summary,
        "action_items":action_items
    }
    return (data) 
    # return dialog
# --- Setup summarization pipeline once ---
summarizer = pipeline(
    "summarization",
    model="philschmid/bart-large-cnn-samsum",
    device=0 if torch.cuda.is_available() else -1
)

def summarize_conversation(dialog_list, max_chunk_chars=4000):
    """
    Summarizes a full conversation (agent and caller) carefully.

    Args:
        dialog_list: List of dialog lines like ["Agent: Hello", "Caller: I need help"]
        max_chunk_chars: Maximum character length per chunk (safe for model input limits)

    Returns:
        A full conversation summary as a string.
    """

    # Merge the conversation into one big text with "Agent:" and "Caller:" markers
    conversation_text = "\n".join(dialog_list)

    # Huggingface models have input size limits, so split if needed
    inputs = []
    current_chunk = ""
    for line in conversation_text.split("\n"):
        if len(current_chunk) + len(line) < max_chunk_chars:
            current_chunk += line + "\n"
        else:
            inputs.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        inputs.append(current_chunk.strip())

    # Summarize each chunk
    summaries = []
    for idx, chunk in enumerate(inputs):
        print(f"Summarizing chunk {idx+1}/{len(inputs)}...")
        summary = summarizer(chunk, max_length=256, min_length=50, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    # Combine all chunk summaries
    final_summary = "\n".join(summaries)
    return final_summary

#action items part
action_verbs = [ "will","verify", "schedule", "send", "update", "confirm", "resolve", "remind"]

# Function to identify action items in the transcript
def extract_action_items_from_transcript(transcript_text):
    """
    Extracts action items from the transcript based on action verbs and their related entities.
    """
    doc = nlp(transcript_text)
    
    # List to store extracted action items
    action_items = []

    # Loop through each sentence in the document
    for sent in doc.sents:
        # Find verbs in the sentence
        verbs = [token for token in sent if token.pos_ == "VERB" and token.lemma_ in action_verbs]
        
        # Check if there are any action verbs in the sentence
        if verbs:
            # Extract direct objects (things being acted upon)
            action_objects = [token for token in sent if token.dep_ in ["dobj", "prep", "attr"]]
            
            # Optionally extract entities (like dates, locations, account info) to filter action items
            entities = [ent for ent in sent.ents]

            # If the sentence contains action verbs and relevant objects or entities, it's an action item
            if action_objects or entities:
                action_items.append(sent.text.strip())

    return action_items

