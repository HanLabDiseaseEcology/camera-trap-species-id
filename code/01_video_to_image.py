import cv2
import os
from glob import glob
import time


start_time = time.perf_counter()


def videos_to_frames_recursive(input_folder, output_root, frame_interval=15):
    # Find AVI files
    video_files = glob(os.path.join(input_folder, '**', '*.mp4'), recursive=True) + \
                  glob(os.path.join(input_folder, '**', '*.avi'), recursive=True) + \
                  glob(os.path.join(input_folder, '**', '*.AVI'), recursive=True) + \
                  glob(os.path.join(input_folder, '**', '*.MP4'), recursive=True)

    print(f"Total videos found: {len(video_files)} in {input_folder}")

    for video_file in video_files:
        # Get relative path to preserve folder structure
        relative_path = os.path.relpath(video_file, input_folder)
        video_name = os.path.splitext(relative_path)[0]
        output_folder = os.path.join(output_root, video_name)

        print(f"\nProcessing video: {video_file}")
        print(f"Saving frames to: {output_folder}")

        video_to_frames(video_file, output_folder, frame_interval)


def video_to_frames(video_path, output_folder, frame_interval=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    if not success:
        print(f"Cannot read video: {video_path}")
        return

    count = 0
    frame_number = 0

    while success:
        if count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"{frame_number:05d}.jpg")
            cv2.imwrite(frame_filename, image)
        success, image = vidcap.read()
        count += 1
        frame_number += 1

    vidcap.release()