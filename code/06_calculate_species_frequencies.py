import os

import pandas as pd


def calculate_species_frequencies(
    input_csv,
    output_folder,
    year,
):
    print(f"Reading best video predictions: {input_csv}")

    predictions_df = pd.read_csv(input_csv)

    if "species" not in predictions_df.columns:
        raise ValueError(
            f"The input CSV does not contain a 'species' column: "
            f"{input_csv}"
        )

    # Clean species names
    predictions_df["species"] = (
        predictions_df["species"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Count the number of rows for each species
    species_frequencies = (
        predictions_df
        .groupby("species")
        .size()
        .reset_index(name="frequency")
        .sort_values(
            "frequency",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    # Remove rows with no species name
    species_frequencies = species_frequencies[
        species_frequencies["species"] != ""
    ]

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    output_csv = os.path.join(
        output_folder,
        f"species_frequency_{year}.csv",
    )

    species_frequencies.to_csv(
        output_csv,
        index=False,
    )

    print(f"Created: {output_csv}")
    print(
        f"Videos counted: "
        f"{species_frequencies['frequency'].sum()}"
    )
    print(
        f"Species categories: "
        f"{len(species_frequencies)}"
    )

    return species_frequencies