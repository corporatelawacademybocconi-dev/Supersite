import pandas as pd

df = pd.read_csv("Scripts/wix_articles_scraped_sample.csv")

print(df.shape)
print(df.columns)
print(df.head())