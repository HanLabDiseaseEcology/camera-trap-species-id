import os

import pandas as pd


def make_video_id(filepath):
    filepath = str(filepath).replace("\\", "/")
    path_parts = filepath.split("/")

    start_index = None

    for index, part in enumerate(path_parts):
        if part.lower().startswith("sector_data_"):
            start_index = index
            break

    if start_index is None:
        return None

    video_parts = path_parts[start_index:]

    # Remove AVI or MP4 extension from the original video filename.
    last_part = video_parts[-1]
    video_parts[-1] = os.path.splitext(last_part)[0]

    return "/".join(video_parts)


def merge_predictions_with_video_metadata(
    predictions_csv,
    metadata_csv,
    output_folder,
    year,
):

    print(f"Reading predictions: {predictions_csv}")
    predictions_df = pd.read_csv(
        predictions_csv,
        low_memory=False,
    )

    print(f"Reading video metadata: {metadata_csv}")
    metadata_df = pd.read_csv(
        metadata_csv,
        low_memory=False,
    )

    if "video_path" not in predictions_df.columns:
        raise ValueError(
            "The predictions CSV does not contain a "
            "'video_path' column."
        )

    if "filepath" not in metadata_df.columns:
        raise ValueError(
            "The metadata CSV does not contain a "
            "'filepath' column."
        )

    # Create the same identifier for both datasets.
    predictions_df["video_id"] = (
        predictions_df["video_path"]
        .apply(make_video_id)
    )

    metadata_df["video_id"] = (
        metadata_df["filepath"]
        .apply(make_video_id)
    )

    # Keep the metadata columns needed for the merge.
    metadata_columns = [
        "video_id",
        "filepath",
        "file_basename",
        "date",
        "time",
    ]

    available_metadata_columns = [
        column
        for column in metadata_columns
        if column in metadata_df.columns
    ]

    metadata_for_merge = metadata_df[
        available_metadata_columns
    ].copy()

    # Rename the original video filepath so it is not confused with the extracted-frame filepath
    metadata_for_merge = metadata_for_merge.rename(
        columns={
            "filepath": "original_video_filepath",
        }
    )

    # Check for duplicate metadata records before merging
    duplicate_video_ids = (
        metadata_for_merge["video_id"]
        .duplicated(keep=False)
        .sum()
    )

    if duplicate_video_ids > 0:
        print(
            f"Warning: {duplicate_video_ids} metadata rows "
            "have duplicate video IDs."
        )

    merged_df = predictions_df.merge(
        metadata_for_merge,
        how="left",
        on="video_id",
        validate="many_to_one",
        indicator=True,
    )

    matched_count = (
        merged_df["_merge"] == "both"
    ).sum()

    unmatched_count = (
        merged_df["_merge"] == "left_only"
    ).sum()

    merged_df = merged_df.drop(
        columns="_merge"
    )

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    output_csv = os.path.join(
        output_folder,
        f"predictions_with_metadata_{year}.csv",
    )

    merged_df.to_csv(
        output_csv,
        index=False,
    )

    print(f"Created: {output_csv}")
    print(f"Predicted videos: {len(predictions_df)}")
    print(f"Videos matched to metadata: {matched_count}")
    print(f"Videos without matching metadata: {unmatched_count}")

    return merged_df