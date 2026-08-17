import os
from datetime import datetime
from glob import glob

import ffmpeg
import pandas as pd


def get_video_date_time(video_path):
    """
    Read the embedded creation date and time from one video.

    Returns None values when the metadata cannot be read.
    """
    try:
        metadata = ffmpeg.probe(video_path)
        first_stream = metadata["streams"][0]
        stream_tags = first_stream.get("tags") or {}

        creation_time = stream_tags.get("creation_time")

        if not creation_time:
            return {
                "date": None,
                "time": None,
            }

        creation_datetime = datetime.fromisoformat(
            creation_time.replace("Z", "+00:00")
        )

        return {
            "date": creation_datetime.strftime("%Y-%m-%d"),
            "time": creation_datetime.strftime("%H:%M:%S"),
        }

    except Exception:
        return {
            "date": None,
            "time": None,
        }


def find_video_files(input_folder):
    """
    Find AVI and MP4 files inside a folder and its subfolders.
    """
    video_files = (
        glob(
            os.path.join(input_folder, "**", "*.MP4"),
            recursive=True,
        )
        + glob(
            os.path.join(input_folder, "**", "*.mp4"),
            recursive=True,
        )
        + glob(
            os.path.join(input_folder, "**", "*.AVI"),
            recursive=True,
        )
        + glob(
            os.path.join(input_folder, "**", "*.avi"),
            recursive=True,
        )
    )

    return video_files


def extract_video_metadata(
    input_folder,
    output_folder,
    year,
):
    """
    Extract embedded metadata from all videos in one yearly folder.
    """
    print(f"Searching for videos in: {input_folder}")

    video_paths = find_video_files(input_folder)

    print(f"Videos found for {year}: {len(video_paths)}")

    rows = []

    for video_path in video_paths:
        date_time = get_video_date_time(video_path)

        rows.append({
            "year": year,
            "filepath": video_path,
            "file_name": os.path.basename(video_path),
            "date": date_time["date"],
            "time": date_time["time"],
        })

    metadata_df = pd.DataFrame(rows)

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    output_csv = os.path.join(
        output_folder,
        f"video_metadata_{year}.csv",
    )

    metadata_df.to_csv(
        output_csv,
        index=False,
    )

    videos_with_time = metadata_df["time"].notna().sum()
    videos_without_time = metadata_df["time"].isna().sum()

    print(f"Created: {output_csv}")
    print(f"Videos with embedded timestamps: {videos_with_time}")
    print(f"Videos missing embedded timestamps: {videos_without_time}")

    return metadata_df