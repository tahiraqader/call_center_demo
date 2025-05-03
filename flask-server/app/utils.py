
# --- Imports ---
import numpy as np
import soundfile as sf
import torch
from io import BytesIO
from faster_whisper import WhisperModel
from transformers import pipeline,  AutoTokenizer, AutoModelForSequenceClassification
import spacy
import numpy as np
import time
from .types import Call

# --- Setup model ONCE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "small"   # Use "tiny" for even faster speeds
model = WhisperModel(model_size, device=device, compute_type="int8" if device == "cpu" else "float16") # used to transcribe
sentiment_model_name = "j-hartmann/emotion-english-distilroberta-base"
#sentiment_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)

# # Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

# # Define a Hugging Face summarization pipeline (optional step for summarizing the call transcript)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

caller_conv = []
agent_conv=[]
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
            caller_conv.append(f"{caller_segs[i][2]}")
            i += 1
        # Otherwise, handle the agent's segment
        else:
            merged_dialog.append(f"Agent: {agent_segs[j][2]}")
            agent_conv.append(f"{agent_segs[j][2]}")
            j += 1

    return merged_dialog
# transcribes the file in dialog format
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
    print(full_dialog)

    return full_dialog


def process_call(audio, sample_rate):
    # run in the following order: transcribe (& diarize), summerize, extract action items.
    start=time.time()
    dialog = transcribe_stereo_file_dialog(audio, sample_rate)
    summary = summarize_conversation(dialog)
    action_items = extract_action_items_from_transcript(summary)
    caller_sentiment, agent_sentiment = sentimentalize_call().values()
    data:call = {
        "dialog": dialog,
        "summary": summary,
        "action_items":action_items,
        "caller_sentiment":caller_sentiment,
        "agent_sentiment":agent_sentiment
    }
    end = time.time()

    print(f"Execution time: {end - start:.2f} seconds")

    return (data) 
   
#create the summerization
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

#action items part -> I expect this words indicates an action should take place
action_verbs = ["contact", "reverse", "resubmit","verify", "schedule", "send", "update", "confirm", "resolve", "remind", "change"]

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

def sentimentalize_call():
    caller_sentiment_summary=sentimentalize_user(caller_conv)
    agent_sentiment_summary=sentimentalize_user(agent_conv)
    return {
        'caller_sentiment' : caller_sentiment_summary,
        'agent_sentiment' : agent_sentiment_summary
    }


def sentimentalize_user(chunks):

  full_text = " ".join(chunks)
  # Split full_text into chunks of max 512 tokens
  max_tokens = 512
  encoded = tokenizer(full_text, return_tensors="pt", truncation=False)
  input_ids = encoded['input_ids'][0]

  # Break into multiple 512-token chunks
  stride = 256  # use stride for overlap
  chunks_input_ids = []
  start = 0
  while start < len(input_ids):
      end = min(start + max_tokens, len(input_ids))
      chunk_ids = input_ids[start:end]
      chunks_input_ids.append(chunk_ids)
      if end == len(input_ids):
          break
      start += stride

  # Aggregate emotion scores
  emotion_scores = {label: 0.0 for label in sentiment_model.config.id2label.values()}
  for chunk_ids in chunks_input_ids:
      inputs = {'input_ids': chunk_ids.unsqueeze(0)}
      with torch.no_grad():
          logits = sentiment_model(**inputs).logits
      probs = torch.nn.functional.softmax(logits, dim=1)[0]
      for i, score in enumerate(probs):
          label = sentiment_model.config.id2label[i]
          emotion_scores[label] += score.item()

  # Normalize scores
  total = sum(emotion_scores.values())
  normalized_emotions = {k: v / total for k, v in emotion_scores.items()}
  sorted_emotions = sorted(normalized_emotions.items(), key=lambda x: x[1], reverse=True)

  # Print top emotion
  top_emotion, top_score = sorted_emotions[0]
  print(f"Dominant emotion: {top_emotion} ({top_score:.2f})")
  return top_emotion