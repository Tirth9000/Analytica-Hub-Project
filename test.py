import pandas as pd

df = pd.read_csv("student_data.csv")

code = """df = df.dropna(subset=["marks"])
print(df["marks"].isnull().sum())
"""

print(df["marks"].isnull().sum())

exec(code)

print(df["marks"].isnull().sum())
