import pandas as pd
import pdfplumber
import re
import os
from collections import defaultdict


# =====================================================
# CLEAN TEXT
# =====================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    # remove line breaks
    text = text.replace("\n", " ")

    # remove weird spaces
    text = text.replace("\u00a0", " ")

    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# COLUMN POSITIONS
# =====================================================

# Adjust these if needed for different PDFs

COLUMN_RANGES = {

    "Activity ID": (0, 90),

    "Activity Name": (90, 380),

    "Start": (380, 460),

    "Finish": (460, 540),

    "BL1 Start": (540, 620),

    "BL1 Finish": (620, 700),

    "Variance": (700, 760),

    "Float": (760, 820),

    "Duration": (820, 880),

    "Activity % Complete": (880, 980),

    "Comments": (980, 1400),
}


# =====================================================
# STANDARD COLUMN NAMES
# =====================================================

COLUMN_ALIASES = {

    "% Complete": "Activity % Complete",

    "Remain Dur": "Duration",

    "Total Float": "Float",

}


# =====================================================
# VALID ACTIVITY REGEX
# =====================================================

ACTIVITY_ID_REGEX = re.compile(r"FER-[A-Z]+-\d+")


# =====================================================
# PDF PROGRAMME PARSER
# =====================================================

def load_pdf_programme(path):

    rows_data = []

    with pdfplumber.open(path) as pdf:

        # ==============================================
        # LOOP THROUGH PAGES
        # ==============================================

        for page in pdf.pages:

            words = page.extract_words(
                use_text_flow=True,
                keep_blank_chars=False
            )

            if not words:
                continue

            # ==========================================
            # GROUP WORDS BY ROW
            # ==========================================

            rows = defaultdict(list)

            for w in words:

                y = round(w["top"], 1)

                rows[y].append(w)

            # ==========================================
            # PROCESS EACH ROW
            # ==========================================

            for y in sorted(rows.keys()):

                row_words = sorted(
                    rows[y],
                    key=lambda x: x["x0"]
                )

                # initialise empty row
                row_dict = {
                    col: [] for col in COLUMN_RANGES
                }

                # ======================================
                # ASSIGN WORDS TO COLUMNS
                # ======================================

                for w in row_words:

                    x = w["x0"]

                    text = clean_text(w["text"])

                    for col, (xmin, xmax) in COLUMN_RANGES.items():

                        if xmin <= x < xmax:

                            row_dict[col].append(text)

                            break

                # ======================================
                # CONVERT LISTS TO STRINGS
                # ======================================

                final_row = {}

                for col, vals in row_dict.items():

                    final_row[col] = clean_text(
                        " ".join(vals)
                    )

                # ======================================
                # VALIDATE ACTIVITY ROW
                # ======================================

                activity_id = final_row["Activity ID"]

                if ACTIVITY_ID_REGEX.match(activity_id):

                    rows_data.append(final_row)

    # =================================================
    # CREATE DATAFRAME
    # =================================================

    df = pd.DataFrame(rows_data)

    # =================================================
    # STANDARDISE COLUMN NAMES
    # =================================================

    df.rename(columns=COLUMN_ALIASES, inplace=True)

    # =================================================
    # ENSURE REQUIRED COLUMNS EXIST
    # =================================================

    required_columns = [

        "Activity ID",

        "Activity Name",

        "Start",

        "Finish",

        "BL1 Start",

        "BL1 Finish",

        "Variance",

        "Float",

        "Duration",

        "Activity % Complete",

        "Comments",
    ]

    for col in required_columns:

        if col not in df.columns:

            df[col] = ""

    # =================================================
    # REORDER COLUMNS
    # =================================================

    df = df[required_columns]

    # =================================================
    # CLEAN FINAL DATAFRAME
    # =================================================

    df = df.fillna("")

    return df


# =====================================================
# UNIVERSAL LOADER
# =====================================================

def load_schedule(path):

    ext = os.path.splitext(path)[1].lower()

    # ==============================================
    # PDF
    # ==============================================

    if ext == ".pdf":

        return load_pdf_programme(path)

    # ==============================================
    # EXCEL
    # ==============================================

    elif ext in [".xlsx", ".xls"]:

        df = pd.read_excel(path, engine="openpyxl")

        df.columns = [
            clean_text(c)
            for c in df.columns
        ]

        return df

    # ==============================================
    # CSV
    # ==============================================

    elif ext == ".csv":

        df = pd.read_csv(path)

        df.columns = [
            clean_text(c)
            for c in df.columns
        ]

        return df

    # ==============================================
    # UNKNOWN
    # ==============================================

    else:

        raise ValueError(
            f"Unsupported file format: {ext}"
        )


# =====================================================
# PROJECT LOADERS
# =====================================================

def load_cl31(path="data/CL31-February.pdf"):

    return load_schedule(path)


def load_cl32(path="data/CL32-May-26.pdf"):

    return load_schedule(path)


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    df = load_cl32()

    print(df.head())

    print("\nColumns:\n")

    print(df.columns.tolist())

    print(f"\nRows extracted: {len(df)}")