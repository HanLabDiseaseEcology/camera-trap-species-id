#!/bin/bash
set -e

# 1 Input/output folders paths
FRAMES_ROOTFOLDER="/Volumes/HAN_LAB_5TB/1fps_video_to_image"
OUTPUT_FOLDER="/Volumes/HAN_LAB_5TB/speciesnet_outputs"

# 2 Create output folders
mkdir -p "$OUTPUT_FOLDER"
mkdir -p "$OUTPUT_FOLDER/logs"
mkdir -p "$OUTPUT_FOLDER/done"

# 3 Run SpeciesNet by folder year
for YEAR in 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023
do
    IMAGE_FOLDER="$FRAMOUTPUT_FOLDERES_ROOT/Sector_Data_$YEAR"
    PREDICTIONS_JSON="$OUTPUT_FOLDER/speciesnet_predictions_$YEAR.json"
    DONE_FILE="$OUTPUT_FOLDER/done/speciesnet_predictions_$YEAR.done"
    LOG_FILE="$OUTPUT_FOLDER/logs/speciesnet_predictions_$YEAR.log"

    echo ""
    echo "Checking $YEAR"

    # Skip missing folders
    if [ ! -d "$IMAGE_FOLDER" ]; then
        echo "Skipping $YEAR: image folder does not exist"
        continue
    fi

    # Skip already completed folders
    if [ -f "$DONE_FILE" ]; then
        echo "Skipping $YEAR: already completed"
        continue
    fi

    echo "Running SpeciesNet for $YEAR"
    echo "Input folder: $IMAGE_FOLDER"
    echo "Output JSON: $PREDICTIONS_JSON"
    echo "Log file: $LOG_FILE"

    # Run SpeciesNet
    python -m speciesnet.scripts.run_model \
        --folders "$IMAGE_FOLDER" \
        --predictions_json "$PREDICTIONS_JSON" \
        --country "USA" \
        --admin1_region "NY" \
        > "$LOG_FILE" 2>&1

    # If folder completed, mark this year done
    touch "$DONE_FILE"

    echo "Finished $YEAR"
done
echo "Finished all available folders that needed species identification"