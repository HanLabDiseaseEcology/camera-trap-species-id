# import pandas as pd

# # Load your human analysis file
# human = pd.read_csv("/Volumes/MICROTUS/CARY_OG_NOEDIT/Sector_Data_2014/2014 Cary_WTD_cameratrap_data_corrected_2-8-2018.csv")

# # Expand each row to every image in its range
# expanded = []
# for idx, row in human.iterrows():
#     # Only expand if both start and end are present and finite
#     if pd.notnull(row['start']) and pd.notnull(row['end']):
#         for img_num in range(int(row['start']), int(row['end']) + 1):
#             img_name = f"IMG_{img_num:04d}.JPG"
#             expanded.append({
#                 'sector': row['sector'],
#                 'date': row['Date'],
#                 'common_name': row['common_name'],
#                 'image': img_name
#             })
#     else:
#         print(f"Skipped row {idx}: start or end is missing.")
# expanded_df = pd.DataFrame(expanded)

# # Load name translation
# translation = pd.read_csv("/Volumes/HAN_LAB_5TB/TEST_analysis/species_id_outputs/NameTranslation.csv")

# # Merge on common_name
# result = expanded_df.merge(translation, how='left', left_on='common_name', right_on='common_name')

# # Now 'species' (the scientific name) from translation is attached
# print(result.head())
# result.to_csv("/Volumes/HAN_LAB_5TB/TEST_analysis/species_id_outputs/human_expanded_with_species.csv", index=False)

# year_from_filename = re.search(r"\d{4}", file_name_base)[0]
# output_csv_name = os.path.join(
#     directory,
#     f"species_id_{year_from_filename}.csv"
# )


########### TESTimport json
########### TEST
import json
import os
import re

import pandas as pd


def normalize_sector(sector_name):
    """
    Convert sector names such as:
        "Sector 10" -> "10"
        "Sector 1n" -> "1N"
        "1 n"       -> "1N"
    """
    sector = sector_name.strip()

    if sector.lower().startswith("sector"):
        sector = sector[len("sector"):].strip()

    sector_match = re.match(r"^(\d+)\s*(.*)$", sector)

    if sector_match:
        sector_number = sector_match.group(1)
        sector_suffix = sector_match.group(2).strip().upper()

        return sector_number + sector_suffix

    return sector


def parse_filepath(filepath):
    path_parts = filepath.replace("\\", "/").split("/")

    year = ""
    season = ""
    sector = ""
    date = ""
    video = ""
    image = os.path.basename(filepath)

    # Find the Sector_Data_YEAR folder
    year_folder_index = None

    for index, folder_name in enumerate(path_parts):
        if folder_name.lower().startswith("sector_data_"):
            year_folder_index = index
            break

    if year_folder_index is not None:
        year_folder = path_parts[year_folder_index]

        year_match = re.search(r"\d{4}", year_folder)

        if year_match:
            year = year_match.group()

        # The first folder after Sector_Data_YEAR is generally
        # the season folder.
        if year_folder_index + 1 < len(path_parts):
            season = path_parts[year_folder_index + 1]

    # Search for the folder whose name begins with "Sector"
    sector_folder_index = None

    for index, folder_name in enumerate(path_parts):
        if folder_name.lower().startswith("sector"):
            # Do not treat Sector_Data_YEAR as the sector folder
            if not folder_name.lower().startswith("sector_data_"):
                sector_folder_index = index
                sector = normalize_sector(folder_name)
                break

    if sector_folder_index is not None:
        # The date folder normally comes immediately after sector
        if sector_folder_index + 1 < len(path_parts):
            date = path_parts[sector_folder_index + 1]

        # Frame extraction creates one folder per original video
        # That folder normally comes immediately after the date
        if sector_folder_index + 2 < len(path_parts):
            video = path_parts[sector_folder_index + 2]

    return {
        "year": year,
        "season": season,
        "sector": sector,
        "date": date,
        "video": video,
        "image": image,
    }


def parse_prediction(prediction_string):
    taxonomy = {
        "class": "",
        "order": "",
        "family": "",
        "genus": "",
        "species": "",
        "common_name": "",
    }

    if not prediction_string:
        return taxonomy

    prediction_parts = prediction_string.split(";")

    if len(prediction_parts) >= 7:
        class_name = prediction_parts[1].strip()
        order_name = prediction_parts[2].strip()
        family_name = prediction_parts[3].strip()
        genus_name = prediction_parts[4].strip()
        species_epithet = prediction_parts[5].strip()
        common_name = prediction_parts[6].strip()

        if genus_name and species_epithet:
            species_name = (
                f"{genus_name.capitalize()} "
                f"{species_epithet.lower()}"
            )
        else:
            species_name = common_name

        taxonomy["class"] = class_name
        taxonomy["order"] = order_name
        taxonomy["family"] = family_name
        taxonomy["genus"] = genus_name
        taxonomy["species"] = species_name
        taxonomy["common_name"] = common_name

    else:
        # Preserve unexpected prediction values rather than losing them
        taxonomy["species"] = prediction_string.strip()

    return taxonomy


def convert_speciesnet_json_to_csv(
    input_json,
    output_csv,
):
    print(f"Reading SpeciesNet JSON: {input_json}")

    with open(input_json, "r") as file:
        data = json.load(file)

    predictions = data.get("predictions", [])

    rows = []
    skipped_metadata_files = 0

    for entry in predictions:
        filepath = entry.get("filepath", "")
        image_name = os.path.basename(filepath)

        # Ignore macOS metadata files such as ._00000.jpg
        if image_name.startswith("._"):
            skipped_metadata_files += 1
            continue

        path_values = parse_filepath(filepath)

        prediction_string = entry.get("prediction", "")
        taxonomy_values = parse_prediction(prediction_string)

        row = {
            "filepath": filepath,
            "year": path_values["year"],
            "season": path_values["season"],
            "sector": path_values["sector"],
            "date": path_values["date"],
            "video": path_values["video"],
            "image": path_values["image"],
            "class": taxonomy_values["class"],
            "order": taxonomy_values["order"],
            "family": taxonomy_values["family"],
            "genus": taxonomy_values["genus"],
            "species": taxonomy_values["species"],
            "common_name": taxonomy_values["common_name"],
            "prediction_score": entry.get("prediction_score"),
        }

        rows.append(row)

    speciesnet_df = pd.DataFrame(rows)

    output_directory = os.path.dirname(output_csv)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    speciesnet_df.to_csv(
        output_csv,
        index=False,
    )

    print(f"Created CSV: {output_csv}")
    print(f"Predictions in JSON: {len(predictions)}")
    print(f"Rows written: {len(speciesnet_df)}")
    print(
        "macOS metadata files skipped: "
        f"{skipped_metadata_files}"
    )

    return speciesnet_df