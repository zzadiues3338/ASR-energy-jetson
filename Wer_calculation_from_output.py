import os
import pandas as pd
import jiwer
from normalizers import EnglishTextNormalizer

# Step 1: Load hypotheses
hypothesis_dir = "/home/chakz/Desktop/outputs"
hypotheses = {}
for filename in os.listdir(hypothesis_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(hypothesis_dir, filename)
        with open(file_path, "r") as file:
            hypotheses[filename[:-4]] = file.read().strip()

# Step 2: Load references
references = {}
reference_file = "/home/chakz/Desktop/dev-clean-2/3752/4944/3752-4944.trans.txt"  # clean or noisy datafile
#reference_file = "/home/chakz/Desktop/longform/combined.txt"  # location of long form audio
with open(reference_file, "r") as file:
    for line in file:
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            references[parts[0]] = parts[1]

# Step 3: Match hypotheses with references and prepare data for WER calculation
data = pd.DataFrame({
    "filename": list(hypotheses.keys()),
    "hypothesis": [hypotheses[fname] for fname in hypotheses.keys()],
    "reference": [references[fname] for fname in hypotheses.keys() if fname in references]
})

# postprocessing : Normalize the texts to ensure apples to apples comparison

normalizer = EnglishTextNormalizer()
data["hypothesis_clean"] = data["hypothesis"].apply(normalizer)
data["reference_clean"] = data["reference"].apply(normalizer)

# Calculate WER

wer = jiwer.wer(list(data["reference_clean"]), list(data["hypothesis_clean"]))
print(f"WER: {wer * 100:.2f} %")
