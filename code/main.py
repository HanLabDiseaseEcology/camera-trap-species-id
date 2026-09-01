import importlib.util
import subprocess
import sys
from pathlib import Path


# ============================================================
# TEST SETTINGS
# ============================================================

YEARS = [2023]

# Test input:
# /Users/liz/Desktop/data_test/Sector_Data_2023
ORIGINAL_VIDEO_ROOT = Path(
    "/Users/liz/Desktop/data_test"
)

# Test outputs
TEST_OUTPUT_ROOT = Path(
    "/Users/liz/Desktop/data_test/output_test"
)

FRAMES_ROOT = TEST_OUTPUT_ROOT / "frames"

SPECIESNET_ROOT = (
    TEST_OUTPUT_ROOT / "speciesnet"
)

CSV_FOLDER = (
    SPECIESNET_ROOT / "csv"
)

FRAME_SUMMARY_FOLDER = (
    SPECIESNET_ROOT / "frame_summaries"
)

BEST_VIDEO_FOLDER = (
    SPECIESNET_ROOT / "best_prediction_per_video"
)

VIDEO_FREQUENCY_FOLDER = (
    SPECIESNET_ROOT / "video_frequencies"
)

VIDEO_METADATA_FOLDER = (
    SPECIESNET_ROOT / "video_metadata"
)

MERGED_FOLDER = (
    SPECIESNET_ROOT / "predictions_with_metadata"
)


# Save every 15th source frame
FRAME_INTERVAL = 15


# ============================================================
# MAIN SCRIPT
# ============================================================


RUN_01_EXTRACT_FRAMES = False
RUN_02_SPECIESNET = False
RUN_03_JSON_TO_CSV = True
RUN_04_FRAME_SUMMARIES = True

RUN_05_BEST_VIDEO_PREDICTION = True
RUN_06_VIDEO_FREQUENCIES = True
RUN_07_VIDEO_METADATA = True
RUN_08_MERGE_METADATA = True


# Rerun 05-08 even if their outputs already exist
SKIP_EXISTING = False


# If the expected output already exists,
# do not rerun that step.
SKIP_EXISTING = False


# ============================================================
# SCRIPT LOCATION
# ============================================================

SCRIPT_FOLDER = Path(
    "/Users/liz/Desktop/species_id_outputs/code"
)


# ============================================================
# LOAD NUMBERED PYTHON SCRIPTS
# ============================================================

def load_script(step_number):
    """
    Find and load the Python script for one numbered step.
    """
    matches = list(
        SCRIPT_FOLDER.glob(f"{step_number}_*.py")
    )

    if len(matches) == 0:
        raise FileNotFoundError(
            f"No Python script found for step {step_number} "
            f"in {SCRIPT_FOLDER}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"More than one Python script found for step "
            f"{step_number}: {matches}"
        )

    script_path = matches[0]

    print(f"Loading: {script_path.name}")

    spec = importlib.util.spec_from_file_location(
        f"script{step_number}",
        script_path,
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


script01 = load_script("01")
script03 = load_script("03")
script04 = load_script("04")
script05 = load_script("05")
script06 = load_script("06")
script07 = load_script("07")
script08 = load_script("08")


# ============================================================
# HELPER
# ============================================================

def should_run(output_path):
    """
    Skip a step when its expected output already exists
    """
    output_path = Path(output_path)

    if SKIP_EXISTING and output_path.exists():
        print(
            f"Already exists. Skipping: {output_path}"
        )
        return False

    return True


# ============================================================
# PIPELINE
# ============================================================

for year in YEARS:

    print()
    print("=" * 60)
    print(f"PROCESSING {year}")
    print("=" * 60)


    # --------------------------------------------------------
    # Paths for specific year
    # --------------------------------------------------------

    original_video_folder = (
        ORIGINAL_VIDEO_ROOT
        / f"Sector_Data_{year}"
    )

    frames_folder = (
        FRAMES_ROOT
        / f"Sector_Data_{year}"
    )

    speciesnet_json = (
        SPECIESNET_ROOT
        / f"speciesnet_predictions_{year}.json"
    )

    species_csv = (
        CSV_FOLDER
        / f"species_id_{year}.csv"
    )

    frame_counts_csv = (
        FRAME_SUMMARY_FOLDER
        / f"species_counts_{year}.csv"
    )

    best_video_csv = (
        BEST_VIDEO_FOLDER
        / f"best_prediction_per_video_{year}.csv"
    )

    frequency_csv = (
        VIDEO_FREQUENCY_FOLDER
        / f"species_frequency_{year}.csv"
    )

    metadata_csv = (
        VIDEO_METADATA_FOLDER
        / f"video_metadata_{year}.csv"
    )

    merged_csv = (
        MERGED_FOLDER
        / f"predictions_with_metadata_{year}.csv"
    )


    # ========================================================
    # 01 Extract frames
    # ========================================================

    if RUN_01_EXTRACT_FRAMES:

        if not original_video_folder.exists():

            print(
                f"01 skipped: original video folder "
                f"not found for {year}: "
                f"{original_video_folder}"
            )

        elif should_run(frames_folder):

            print("01 Extracting frames")

            script01.videos_to_frames_recursive(
                str(original_video_folder),
                str(frames_folder),
                frame_interval=FRAME_INTERVAL,
            )


    # ========================================================
    # 02 Run SpeciesNet
    # ========================================================

    if RUN_02_SPECIESNET:

        if not frames_folder.exists():

            print(
                f"02 skipped: frame folder "
                f"not found for {year}"
            )

        elif should_run(speciesnet_json):

            print("02 Running SpeciesNet")

            SPECIESNET_ROOT.mkdir(
                parents=True,
                exist_ok=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "speciesnet.scripts.run_model",
                    "--folders",
                    str(frames_folder),
                    "--predictions_json",
                    str(speciesnet_json),
                    "--country",
                    "USA",
                    "--admin1_region",
                    "NY",
                ],
                check=True,
            )


    # ========================================================
    # 03 Convert JSON to CSV
    # ========================================================

    if RUN_03_JSON_TO_CSV:

        if not speciesnet_json.exists():

            print(
                f"03 skipped: SpeciesNet JSON "
                f"not found for {year}"
            )

        elif should_run(species_csv):

            print("03 Converting JSON to CSV")

            script03.convert_speciesnet_json_to_csv(
                input_json=str(speciesnet_json),
                output_csv=str(species_csv),
            )


    # ========================================================
    # 04 Frame-level summaries
    # ========================================================

    if RUN_04_FRAME_SUMMARIES:

        if not species_csv.exists():

            print(
                f"04 skipped: SpeciesNet CSV "
                f"not found for {year}"
            )

        elif should_run(frame_counts_csv):

            print(
                "04 Creating frame-level summaries"
            )

            script04.summarize_speciesnet_results(
                input_csv=str(
                    species_csv
                ),
                output_folder=str(
                    FRAME_SUMMARY_FOLDER
                ),
                year=year,
            )


    # ========================================================
    # 05 Best prediction per video
    # ========================================================

    if RUN_05_BEST_VIDEO_PREDICTION:

        if not species_csv.exists():

            print(
                f"05 skipped: SpeciesNet CSV "
                f"not found for {year}"
            )

        elif should_run(best_video_csv):

            print(
                "05 Selecting best prediction per video"
            )

            script05.select_best_prediction_per_video(
                input_csv=str(
                    species_csv
                ),
                output_folder=str(
                    BEST_VIDEO_FOLDER
                ),
                year=year,
            )


    # ========================================================
    # 06 Video-level species frequencies
    # ========================================================

    if RUN_06_VIDEO_FREQUENCIES:

        if not best_video_csv.exists():

            print(
                f"06 skipped: best-video CSV "
                f"not found for {year}"
            )

        elif should_run(frequency_csv):

            print(
                "06 Calculating video-level frequencies"
            )

            script06.calculate_species_frequencies(
                input_csv=str(
                    best_video_csv
                ),
                output_folder=str(
                    VIDEO_FREQUENCY_FOLDER
                ),
                year=year,
            )

# ========================================================
# 07 Extract timestamps from first video frame
# ========================================================

if RUN_07_VIDEO_METADATA:

    if not frames_folder.exists():

        print(
            f"07 skipped: frame folder "
            f"not found for {year}: "
            f"{frames_folder}"
        )

    elif should_run(metadata_csv):

        print(
            "07 Extracting timestamps from video frames"
        )

        script07.extract_video_metadata(
            input_folder=str(
                frames_folder
            ),
            output_folder=str(
                VIDEO_METADATA_FOLDER
            ),
            year=year,
        )

    # ========================================================
    # 08 Merge predictions with metadata
    # ========================================================

    if RUN_08_MERGE_METADATA:

        if not best_video_csv.exists():

            print(
                f"08 skipped: best-video CSV "
                f"not found for {year}"
            )

        elif not metadata_csv.exists():

            print(
                f"08 skipped: metadata CSV "
                f"not found for {year}"
            )

        elif should_run(merged_csv):

            print(
                "08 Merging predictions with timestamps"
            )

            script08.merge_predictions_with_video_metadata(
                predictions_csv=str(
                    best_video_csv
                ),
                metadata_csv=str(
                    metadata_csv
                ),
                output_folder=str(
                    MERGED_FOLDER
                ),
                year=year,
            )


print()
print("=" * 60)
print("TEST PIPELINE FINISHED")
print("=" * 60)
