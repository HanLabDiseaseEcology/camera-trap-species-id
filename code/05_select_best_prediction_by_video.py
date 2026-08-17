import os
import pandas as pd

BAD_VALUES = {
    "",
    "no cv result",
    "no cv result no cv result",
    "blank",
}

def clean_text_series(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

def select_best_prediction_per_video(
    input_csv,
    output_folder,
    year,
):
    print(f"Reading frame predictions: {input_csv}")

    speciesnet_df = pd.read_csv(
        input_csv,
        low_memory=False,
    )

    required_columns = {
        "filepath",
        "class",
        "order",
        "genus",
        "species",
        "prediction_score",
    }

    missing_columns = (
        required_columns
        - set(speciesnet_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"The input CSV is missing columns: "
            f"{sorted(missing_columns)}"
        )

    speciesnet_df.columns = [
        str(column).strip()
        for column in speciesnet_df.columns
    ]

    # The parent folder of each frame is the original video folder.
    speciesnet_df["video_path"] = (
        speciesnet_df["filepath"]
        .apply(os.path.dirname)
    )

    speciesnet_df["prediction_score"] = (
        pd.to_numeric(
            speciesnet_df["prediction_score"],
            errors="coerce",
        )
    )

    taxonomy_columns = [
        "class",
        "order",
        "genus",
        "species",
    ]

    cleaned_taxonomy = pd.DataFrame({
        column: clean_text_series(
            speciesnet_df[column]
        )
        for column in taxonomy_columns
    })

    # Keep a row if at least one taxonomy column contains a usable classification
    valid_taxonomy = (
        ~cleaned_taxonomy.isin(BAD_VALUES)
    )

    eligible_predictions = speciesnet_df[
        valid_taxonomy.any(axis=1)
    ].copy()

    if eligible_predictions.empty:
        best_predictions = eligible_predictions
    else:
        best_row_indexes = (
            eligible_predictions
            .groupby("video_path")["prediction_score"]
            .idxmax()
        )

        best_predictions = (
            eligible_predictions
            .loc[best_row_indexes]
            .sort_values("video_path")
            .reset_index(drop=True)
        )

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    output_csv = os.path.join(
        output_folder,
        f"best_prediction_per_video_{year}.csv",
    )

    best_predictions.to_csv(
        output_csv,
        index=False,
    )

    print(f"Created: {output_csv}")
    print(
        f"Frame predictions read: "
        f"{len(speciesnet_df)}"
    )
    print(
        f"Videos retained: "
        f"{len(best_predictions)}"
    )

    return best_predictions