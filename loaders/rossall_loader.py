def load_rossall():

    base = "data/Rossall/"

    cl31_path = os.path.join(base, "CL31.pdf")
    cl32_path = os.path.join(base, "CL32.pdf")

    cl31 = extract_pdf_table(cl31_path)
    cl31 = clean(cl31)
    cl31 = clean_dates(cl31)
    cl31 = clean_duration(cl31)

    cl32 = extract_pdf_table(cl32_path)
    cl32 = clean(cl32)
    cl32 = clean_dates(cl32)
    cl32 = clean_duration(cl32)

    return cl31, cl32
