import csv
with open("similarity_scores.csv", "r", encoding="utf-8") as f:
    r = csv.reader(f, quotechar='"', doublequote=True, skipinitialspace=False)
    header = next(r)
    print("Header len:", len(header))
    row = next(r)
    print("Row len:", len(row))
    for i, c in enumerate(row):
        print("col", i, "len=", len(c))
        # Show full first col to see if it's complete JSON
        if i == 0:
            import json
            try:
                j = json.loads(c)
                print("  col0 is valid JSON, len=", len(j))
            except Exception as e:
                print("  col0 JSON error:", e)
        if i == 2:
            try:
                f = float(c.strip())
                print("  col2 is float:", f)
            except Exception as e:
                print("  col2 float error:", e)
