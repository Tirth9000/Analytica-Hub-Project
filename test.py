import pandas as pd

df = pd.read_csv("medical_students_dataset.csv")

rows = df.values.tolist()  
print(len(rows))

