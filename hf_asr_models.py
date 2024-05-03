#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 22:54:05 2024

@author: chakz
"""

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import os
import time 
model_id = "distil-whisper/distil-large-v2"
# Directory containing .flac files
directory = "/home/chakz/Desktop/dev-clean-2/3752/4944"




device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32


model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

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

# Process each file
t_in = time.time()
results = {}
for filename in os.listdir(directory):
    if filename.endswith(".flac"):
        file_path = os.path.join(directory, filename)
        audio_input, sample_rate = sf.read(file_path)
        result = pipe(audio_input)
        transcription = result["text"]
        results[filename] = transcription
t_out = time.time()

print(t_out-t_in)


# Print all results
for filename, transcription in results.items():
    print(f"{filename}: {transcription}")
    
# get the accuracy metrics and save output     