import os
import re
from datetime import datetime
from glob import glob

import cv2
import pandas as pd
import pytesseract


pytesseract.pytesseract.tesseract_cmd = (
    "/opt/homebrew/bin/tesseract"
)


def get_video_date_time(image_path):
    """
    Read the burned-in date and time from one extracted video frame.

    Returns None values when the timestamp cannot be read.
    """
    try:
        image = cv2.imread(image_path)

        if image is None:
            print(f"Could not read image: {image_path}")

            return {
                "date": None,
                "time": None,
            }

        height, width = image.shape[:2]

        # Timestamp is in the bottom portion of the frame.
        crop_height = int(height * 0.08)

        timestamp_area = image[
            height - crop_height:height,
            0:width,
        ]

        text = pytesseract.image_to_string(
            timestamp_area,
            config="--psm 6",
        )

        text = text.strip().upper()
        text = re.sub(r"\s+", " ", text)

        timestamp_pattern = (
            r"(\d{1,2})/(\d{1,2})/(\d{4})"
            r"\s+"
            r"(\d{1,2}):(\d{2})"
            r"\s*(AM|PM)"
        )

        match = re.search(
            timestamp_pattern,
            text,
            re.IGNORECASE,
        )

        if not match:
            print(f"No timestamp found: {image_path}")
            print(f"OCR text: {text}")

            return {
                "date": None,
                "time": None,
            }

        timestamp_text = (
            f"{match.group(1)}/"
            f"{match.group(2)}/"
            f"{match.group(3)} "
            f"{match.group(4)}:"
            f"{match.group(5)}"
            f"{match.group(6)}"
        )

        creation_datetime = datetime.strptime(
            timestamp_text,
            "%m/%d/%Y %I:%M%p",
        )

        return {
            "date": creation_datetime.strftime("%Y-%m-%d"),
            "time": creation_datetime.strftime("%H:%M:%S"),
        }

    except Exception as error:
        print(f"Could not read timestamp: {image_path}")
        print(error)

        return {
            "date": None,
            "time": None,
        }


def find_video_frames(input_folder):
    """
    Find the first extracted frame from each video folder.
    """
    frame_files = glob(
        os.path.join(
            input_folder,
            "**",
            "00000.jpg",
        ),
        recursive=True,
    )

    return frame_files


def extract_video_metadata(
    input_folder,
    output_folder,
    year,
):
    """
    Extract burned-in timestamps from the first frame
    of each video folder.
    """
    print(f"Searching for video frames in: {input_folder}")

    frame_paths = find_video_frames(input_folder)

    print(f"Video frames found for {year}: {len(frame_paths)}")
    print(f"First few frame paths: {frame_paths[:5]}")

    rows = []

    for frame_path in frame_paths:
        date_time = get_video_date_time(frame_path)

        # The parent folder represents the original video.
        video_path = os.path.dirname(frame_path)

        rows.append({
            "year": year,
            "filepath": video_path,
            "file_name": os.path.basename(video_path),
            "date": date_time["date"],
            "time": date_time["time"],
        })

    metadata_df = pd.DataFrame(
        rows,
        columns=[
            "year",
            "filepath",
            "file_name",
            "date",
            "time",
        ],
    )

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
    print(
        f"Videos with timestamps: "
        f"{videos_with_time}"
    )
    print(
        f"Videos missing timestamps: "
        f"{videos_without_time}"
    )

    return metadata_df