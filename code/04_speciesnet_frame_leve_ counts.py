import os

import pandas as pd


def count_species_occurrences(df, species_col="species"):
    return (
        df[species_col]
        .dropna()
        .value_counts()
        .rename_axis("species")
        .reset_index(name="count")
    )


def species_percentage(df, species_col="species"):

    species = (
        df[species_col]
        .astype("string")
        .str.strip()
    )
    valid_species = species[
        species.notna()
        & (species != "")
        & (species.str.lower() != "blank")
    ]
    counts = (
        valid_species
        .value_counts()
        .rename_axis("species")
        .reset_index(name="count")
    )
    total = counts["count"].sum()
    if total == 0:
        counts["percentage"] = 0.0
    else:
        counts["percentage"] = (
            counts["count"] / total * 100
        )
    return counts
def species_monthly_percentage(
    df,
    date_col="date",
    species_col="species",
):
    data = df.copy()
    data[date_col] = pd.to_datetime(
        data[date_col],
        errors="coerce",
    )
    data[species_col] = (
        data[species_col]
        .astype("string")
        .str.strip()
    )
    data = data[
        data[date_col].notna()
        & data[species_col].notna()
        & (data[species_col] != "")
        & (data[species_col].str.lower() != "blank")
    ].copy()
    data["month"] = (
        data[date_col]
        .dt.to_period("M")
        .astype(str)
    )
    summary = (
        data.groupby(["month", species_col])
        .size()
        .reset_index(name="count")
    )
    summary["monthly_total"] = (
        summary.groupby("month")["count"]
        .transform("sum")
    )
    summary["percentage"] = (
        summary["count"]
        / summary["monthly_total"]
        * 100
    )
    return summary.sort_values(
        ["month", "count"],
        ascending=[True, False],
    )

def summarize_speciesnet_results(
    input_csv,
    output_folder,
    year,
):
    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    print(f"Reading SpeciesNet results: {input_csv}")

    speciesnet_df = pd.read_csv(input_csv)

    if "species" not in speciesnet_df.columns:
        raise ValueError(
            f"The input CSV does not contain a 'species' column: "
            f"{input_csv}"
        )

    species_counts = count_species_occurrences(
        speciesnet_df
    )

    species_percentages = species_percentage(
        speciesnet_df
    )

    counts_output = os.path.join(
        output_folder,
        f"species_counts_{year}.csv",
    )

    percentages_output = os.path.join(
        output_folder,
        f"species_percentages_{year}.csv",
    )

    species_counts.to_csv(
        counts_output,
        index=False,
    )

    species_percentages.to_csv(
        percentages_output,
        index=False,
    )

    print(f"Created: {counts_output}")
    print(f"Created: {percentages_output}")

    if "date" in speciesnet_df.columns:
        monthly_percentages = (
            species_monthly_percentage(
                speciesnet_df
            )
        )

        monthly_output = os.path.join(
            output_folder,
            f"species_monthly_percentages_{year}.csv",
        )

        monthly_percentages.to_csv(
            monthly_output,
            index=False,
        )

        print(f"Created: {monthly_output}")

    else:
        print(
            f"Monthly summary skipped for {year}: "
            "the input CSV does not contain a date column."
        )

    print(
        f"Total predictions for {year}: "
        f"{len(speciesnet_df)}"
    )

    print("\nMost common predictions:")
    print(species_counts.head(10))

    return {
        "species_counts": species_counts,
        "species_percentages": species_percentages,
    }