import pandas as pd

# Sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
}

# Create DataFrame
df = pd.DataFrame(data)

# Define allowed variables for exec environment
exec_env = {
    'df': df,
    'pd': pd
}

# Example user command
command = """df = df.drop(columns=['salary'])
print(df)"""

# Execute the command
exec(command, {}, exec_env)

# Show result
print(exec_env['df'])
