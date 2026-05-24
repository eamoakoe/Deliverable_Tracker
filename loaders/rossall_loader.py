import os

def load_rossall():

    base = "data/Rossall/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    # ✅ CL31
    cl31 = extract_pdf_table(cl31_path)
    cl31 = clean(cl31)

    # ✅ CL32
    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)

    return cl31, cl32