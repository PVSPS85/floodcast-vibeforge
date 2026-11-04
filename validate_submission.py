#!/usr/bin/env python3
"""
validate_submission.py
Strict integrity verification for predictions.csv in the FloodCast hackathon.

Verifies:
1. File exists and is non-empty.
2. Exact column headers match station_id, date, discharge_cfs.
3. Row count matches data/test.csv exactly.
4. No null, NaN, or infinite values.
5. No negative discharge predictions (discharge_cfs >= 0).
6. Dates strictly adhere to YYYY-MM-DD format.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import numpy as np
import pandas as pd


EXPECTED_COLUMNS: List[str] = ["station_id", "date", "discharge_cfs"]
DATE_REGEX: re.Pattern = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")


class SubmissionValidator:
    def __init__(
        self,
        submission_path: str = "predictions.csv",
        test_path: str = "data/test.csv",
    ) -> None:
        self.submission_path = Path(submission_path)
        self.test_path = Path(test_path)
        self.checks: List[Tuple[str, bool, str]] = []
        self.df: pd.DataFrame = pd.DataFrame()
        self.test_df: pd.DataFrame = pd.DataFrame()

    def record_check(self, name: str, passed: bool, message: str) -> None:
        self.checks.append((name, passed, message))

    def run_all_checks(self) -> bool:
        print("=" * 65)
        print(f"RUNNING SUBMISSION INTEGRITY CHECKS: {self.submission_path}")
        print("=" * 65)

        # 1. File exists and is non-empty
        if not self.submission_path.exists():
            self.record_check("File Exists & Non-Empty", False, f"File not found: {self.submission_path}")
            self.print_summary()
            return False

        file_size = os.path.getsize(self.submission_path)
        if file_size == 0:
            self.record_check("File Exists & Non-Empty", False, "File is completely empty (0 bytes).")
            self.print_summary()
            return False

        self.record_check(
            "File Exists & Non-Empty",
            True,
            f"File exists ({file_size:,} bytes).",
        )

        # Load CSV
        try:
            self.df = pd.read_csv(self.submission_path, dtype={"station_id": str, "date": str})
        except Exception as e:
            self.record_check("CSV Readable", False, f"Failed to parse CSV: {e}")
            self.print_summary()
            return False

        # 2. Exact column headers
        actual_cols = list(self.df.columns)
        if actual_cols == EXPECTED_COLUMNS:
            self.record_check(
                "Exact Column Headers",
                True,
                f"Columns match expected: {EXPECTED_COLUMNS}",
            )
        else:
            self.record_check(
                "Exact Column Headers",
                False,
                f"Expected {EXPECTED_COLUMNS}, but found {actual_cols}",
            )

        # 3. Row count matches data/test.csv
        if not self.test_path.exists():
            self.record_check(
                "Row Count Match",
                False,
                f"Reference test file {self.test_path} not found.",
            )
        else:
            try:
                self.test_df = pd.read_csv(self.test_path, dtype={"station_id": str, "date": str})
                expected_rows = len(self.test_df)
                actual_rows = len(self.df)
                if actual_rows == expected_rows:
                    self.record_check(
                        "Row Count Match",
                        True,
                        f"Row count matches test.csv exactly ({actual_rows:,} rows).",
                    )
                else:
                    self.record_check(
                        "Row Count Match",
                        False,
                        f"Expected {expected_rows:,} rows, but got {actual_rows:,} rows.",
                    )
            except Exception as e:
                self.record_check("Row Count Match", False, f"Error reading {self.test_path}: {e}")

        # 4. No null, NaN, or infinite values
        total_nulls = int(self.df.isna().sum().sum())
        discharge_col = self.df["discharge_cfs"] if "discharge_cfs" in self.df.columns else None

        has_inf = False
        if discharge_col is not None and pd.api.types.is_numeric_dtype(discharge_col):
            has_inf = bool(np.isinf(discharge_col.to_numpy()).any())

        if total_nulls == 0 and not has_inf:
            self.record_check(
                "No Null / NaN / Inf",
                True,
                "Zero nulls, NaNs, or infinite values detected across all columns.",
            )
        else:
            self.record_check(
                "No Null / NaN / Inf",
                False,
                f"Found {total_nulls} null/NaN values and has_inf={has_inf}.",
            )

        # 5. No negative discharge predictions (discharge_cfs >= 0)
        if discharge_col is not None:
            try:
                num_discharge = pd.to_numeric(discharge_col, errors="coerce")
                if num_discharge.isna().any():
                    self.record_check(
                        "Non-Negative Discharge",
                        False,
                        "discharge_cfs contains non-numeric entries.",
                    )
                else:
                    negative_count = int((num_discharge < 0.0).sum())
                    if negative_count == 0:
                        min_val = num_discharge.min()
                        max_val = num_discharge.max()
                        self.record_check(
                            "Non-Negative Discharge",
                            True,
                            f"All predictions >= 0.0 (Min: {min_val:.2f}, Max: {max_val:.2f} cfs).",
                        )
                    else:
                        self.record_check(
                            "Non-Negative Discharge",
                            False,
                            f"Found {negative_count} negative discharge predictions!",
                        )
            except Exception as e:
                self.record_check("Non-Negative Discharge", False, f"Validation error: {e}")
        else:
            self.record_check("Non-Negative Discharge", False, "Missing 'discharge_cfs' column.")

        # 6. Dates follow YYYY-MM-DD format
        if "date" in self.df.columns:
            date_series = self.df["date"].astype(str)
            regex_matches = date_series.str.match(DATE_REGEX)
            all_regex_match = bool(regex_matches.all())

            # Verify calendar date validity via pd.to_datetime
            try:
                parsed_dates = pd.to_datetime(date_series, format="%Y-%m-%d", errors="raise")
                calendar_valid = True
            except Exception:
                calendar_valid = False

            if all_regex_match and calendar_valid:
                min_d = date_series.min()
                max_d = date_series.max()
                self.record_check(
                    "Date Format (YYYY-MM-DD)",
                    True,
                    f"All dates strictly conform to YYYY-MM-DD ({min_d} to {max_d}).",
                )
            else:
                invalid_count = int((~regex_matches).sum())
                self.record_check(
                    "Date Format (YYYY-MM-DD)",
                    False,
                    f"Found {invalid_count} dates that violate YYYY-MM-DD format.",
                )
        else:
            self.record_check("Date Format (YYYY-MM-DD)", False, "Missing 'date' column.")

        # 7. Alignment check with test.csv (station_id and date sequence)
        if not self.test_df.empty and "station_id" in self.df.columns and "date" in self.df.columns:
            stations_match = bool((self.df["station_id"] == self.test_df["station_id"]).all())
            dates_match = bool((self.df["date"] == self.test_df["date"]).all())
            if stations_match and dates_match:
                self.record_check(
                    "Station & Date Alignment",
                    True,
                    "Predictions align row-for-row with test.csv stations and dates.",
                )
            else:
                self.record_check(
                    "Station & Date Alignment",
                    False,
                    f"Alignment mismatch: stations_match={stations_match}, dates_match={dates_match}.",
                )

        return self.print_summary()

    def print_summary(self) -> bool:
        all_passed = True
        for i, (name, passed, msg) in enumerate(self.checks, 1):
            status = "[ PASS ]" if passed else "[ FAIL ]"
            print(f"{i}. {status} {name}")
            print(f"      -> {msg}")
            if not passed:
                all_passed = False

        print("=" * 65)
        if all_passed:
            print(">>> FINAL RESULT: ALL INTEGRITY CHECKS PASSED. READY FOR SUBMISSION. <<<")
        else:
            print(">>> FINAL RESULT: VALIDATION FAILED. PLEASE FIX IDENTIFIED ISSUES. <<<")
        print("=" * 65)
        return all_passed


def main() -> None:
    sub_path = sys.argv[1] if len(sys.argv) > 1 else "predictions.csv"
    test_path = sys.argv[2] if len(sys.argv) > 2 else "data/test.csv"

    validator = SubmissionValidator(submission_path=sub_path, test_path=test_path)
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

