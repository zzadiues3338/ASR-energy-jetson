#!/bin/bash

# Define the models and compute types
declare -a models=("tiny", "small", "base", "medium")
declare -a compute_types=("--compute_type float32", "--compute_type float16", "--compute_type int8")

# Loop through each combination of model and compute type
for model in "${models[@]}"; do
    for compute_type in "${compute_types[@]}"; do
        # Call the run_single_experiment.sh script with the current model and compute type
        ./run_single_experiment.sh "$model" "$compute_type"
    done
done

