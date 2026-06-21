import pandas as pd

df = pd.read_csv("Scripts/wix_articles_scraped_sample.csv")

empty = df[df["content"].isna() | (df["content"].astype(str).str.strip() == "")]

print(f"Empty articles: {len(empty)}")
print(empty[["title", "old_url"]])