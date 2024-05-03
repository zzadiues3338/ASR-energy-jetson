import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import os
import time 

#model_id = "distil-whisper/distil-large-v2"
#model_id = "distil-whisper/distil-medium.en"
model_id = "distil-whisper/distil-small.en"

# Directory containing .flac files
directory = "/home/chakz/Desktop/dev-clean-2/3752/4944"

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32


model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
).to(device)


processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    torch_dtype=torch_dtype,
    device=device,
)

input_directory = "/home/chakz/Desktop/dev-clean-2/3752/4944"

output_directory = "/home/chakz/Desktop/output_hf"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

results = {}
for filename in sorted(os.listdir(input_directory)):  # Sort filenames to process in order
    if filename.endswith(".flac"):
        file_path = os.path.join(input_directory, filename)
        audio_input, sample_rate = sf.read(file_path)
        result = pipe(audio_input)
        transcription = result["text"]
        results[filename] = transcription

        # Create a text file for each transcription
        output_file_path = os.path.join(output_directory, f"{filename[:-5]}.txt")  # Removes .flac and adds .txt
        with open(output_file_path, 'w') as text_file:
            text_file.write(transcription)

