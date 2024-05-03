#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 00:39:10 2024

@author: chakz
"""

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import os
import time 
from transformers import AutoProcessor, WavLMForCTC


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32


# processor = AutoProcessor.from_pretrained("facebook/wav2vec2-base-960h")
# model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h").to(device).to(torch_dtype)  # Convert model to float16

processor = AutoProcessor.from_pretrained("patrickvonplaten/wavlm-libri-clean-100h-base-plus")
model = WavLMForCTC.from_pretrained("patrickvonplaten/wavlm-libri-clean-100h-base-plus").to(device).to(torch_dtype)

total_parameters = sum(p.numel() for p in model.parameters())

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

