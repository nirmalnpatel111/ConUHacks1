import pandas as pd

# Load the data
input_file = 'one.csv'  # Replace with the name of your input CSV file
output_file = 'merged_output.csv'  # Name of the output CSV file

# Read the CSV file into a DataFrame
df = pd.read_csv(input_file)

# Merge rows by grouping and summing amounts
merged_df = (
    df.groupby(['Nom_Intersection', 'Date', 'Description_Code_Banque'])
    .agg({
        'Amount': 'sum', 
        'Longitude': 'first', 
        'Latitude': 'first'
    })
    .reset_index()
)

# Save the merged data to a new CSV file
merged_df.to_csv(output_file, index=False)

print(f"Merged data has been saved to '{output_file}'")
