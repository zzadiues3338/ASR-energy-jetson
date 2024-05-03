#!/bin/bash

# Define a variable with the current datetime to use in filenames
CURRENT_DATETIME=$(date +%Y-%m-%d_%H-%M-%S)

# Start tegrastats and log output to a file with datetime in its name. Run in background.
TEGRASTATS_LOGFILE="teg_trials_$CURRENT_DATETIME.csv"
sudo tegrastats --logfile $TEGRASTATS_LOGFILE &

# Ensure the Docker image tag is captured correctly
IMAGE_TAG=$(autotag whisperx | grep -o 'dustynv/whisperx:[^ ]*' | tail -1)
echo "Using Docker Image Tag: $IMAGE_TAG"

# Start the Docker container in detached mode and capture the full container ID
FULL_OUTPUT=$(jetson-containers run -d -v /home/chakz/Desktop/dev-clean-2/3752/4944:/app/audio -v /home/chakz/Desktop/outputs:/app/outputs $IMAGE_TAG)
CONTAINER_ID=$(echo "$FULL_OUTPUT" | grep -o '[a-f0-9]\{64\}')
SHORT_CONTAINER_ID=$(echo "$CONTAINER_ID" | cut -c 1-12)

echo "Full Container ID: $CONTAINER_ID"
echo "Short Container ID: $SHORT_CONTAINER_ID"

# Define the model name and additional kwargs dynamically
MODEL_NAME="base"
EXTRA_KWARGS=""  # Example, replace or dynamically capture

# Wait for the container to be fully up and running
sleep 4

# Execute the whisperx command inside the running container and measure the time
echo "Executing whisperx command inside the container using model $MODEL_NAME..."
TIME_FILE="time_$CURRENT_DATETIME.txt"
{ time docker exec $CONTAINER_ID bash -c "whisperx /app/audio/*.flac --model $MODEL_NAME --output_dir /app/outputs --output_format txt --no_align $EXTRA_KWARGS" ; } 2> $TIME_FILE

# Extract the real time used by the command from the output
EXEC_TIME=$(grep real $TIME_FILE | awk '{print $2}')
rm $TIME_FILE

# Stop the Docker container
echo "Stopping container..."
docker stop $CONTAINER_ID

INTERMEDIATE_FILE="tmp_$CURRENT_DATETIME.txt"
cat $TEGRASTATS_LOGFILE | tr -s ' ' ',' > $INTERMEDIATE_FILE  
# Part 2: Replace "%@" with commas for the final output file
OUTPUT_FILE="output_$CURRENT_DATETIME.csv"
cat $INTERMEDIATE_FILE | tr -s "%@" ',' > "$OUTPUT_FILE"

# Optional: Cleanup temporary and intermediate files
rm $INTERMEDIATE_FILE


# Execute the Python script for power report and capture its output
PYTHON_OUTPUT=$(python ./process_power_report_jp51.py "$OUTPUT_FILE")

# Execute the Python script for WER calculation and capture its output
WER_OUTPUT=$(python Wer_calculation_from_output.py)
WER=$(echo "$WER_OUTPUT" | grep 'WER' | awk '{print $2}')


# Extract values from the Python script's output
TOTAL_ENERGY_JOULE=$(echo "$PYTHON_OUTPUT" | grep 'TOTAL_ENERGY_JOULE' | cut -d'=' -f2)
MAX_VALUE=$(echo "$PYTHON_OUTPUT" | grep 'MAX_VALUE' | cut -d'=' -f2)

# Prepare and log all data including execution time, WER, and power metrics on one line
ADDITIONAL_INFO=$(echo $EXTRA_KWARGS | sed 's/--//g' | awk '{for (i=1; i<=NF; i+=2) printf $i "=" $(i+1) " "}')
LOG_ENTRY="Output File: $OUTPUT_FILE, Execution Time: $EXEC_TIME, WER: $WER, Total Energy Used (Joules): $TOTAL_ENERGY_JOULE, Max Mem MB: $MAX_VALUE, Model Info: $MODEL_NAME, $ADDITIONAL_INFO"
LOG_FILE="process_log.txt"
echo "$LOG_ENTRY" >> "$LOG_FILE"

# Completion message
echo "Script execution completed. Power consumption and performance metrics output saved to $OUTPUT_FILE. Log details added to $LOG_FILE."

