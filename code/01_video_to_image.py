import cv2
import os
from glob import glob
import time


start_time = time.perf_counter()
def videos_to_frames_recursive(input_folder, output_root, frame_interval=15):
    # Find AVI files (case-insensitive)
    video_files = glob(os.path.join(input_folder, '**', '*.mp4'), recursive=True) + \
                  glob(os.path.join(input_folder, '**', '*.avi'), recursive=True)

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

# Paths configuration
base_input_path = "/Volumes/MICROTUS/CARY_OG_NOEDIT/Sector_Data_"
base_output_path = "/Volumes/HAN_LAB_5TB/1fps_video_to_image"
years = range(2023, 2024)

for year in years:
    input_path = f"{base_input_path}{year}"
    output_path = os.path.join(base_output_path, f"Sector_Data_{year}")

    if os.path.exists(input_path):
        print(f"\n=== Processing Year: {year} ===")
        print("Input Path:", input_path)
        print("Output Path:", output_path)

        videos_to_frames_recursive(input_path, output_path, frame_interval=15)
    else:
        print(f"\nDirectory does NOT exist for year {year}: {input_path}")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Function executed in {elapsed_time:.4f} seconds")