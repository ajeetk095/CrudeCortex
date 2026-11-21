"""Regenerate the sterilized dataset + dictionary + cleaning log from raw data.
Run:  python scripts/sterilize_data.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics import (PROJECT_ROOT, build_research_data, data_dictionary_df)


def main() -> None:
    rd = build_research_data()
    out = os.path.join(PROJECT_ROOT, "data")
    rd.sterilized.to_csv(os.path.join(out, "sterilized_data.csv"))
    rd.outlier_log.to_csv(os.path.join(out, "cleaning_log.csv"), index=False)
    data_dictionary_df().to_csv(os.path.join(out, "data_dictionary.csv"), index=False)
    print(f"sterilized_data.csv  {rd.sterilized.shape}")
    print(f"cleaning_log.csv     {len(rd.outlier_log)} entries")
    print(f"data_dictionary.csv  {len(data_dictionary_df())} variables")
    print("Raw data preserved untouched at data/raw_data.csv")


if __name__ == "__main__":
    main()
