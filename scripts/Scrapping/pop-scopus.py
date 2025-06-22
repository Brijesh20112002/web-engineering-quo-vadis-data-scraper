import pandas as pd

# Read both CSV files with UTF-8-SIG encoding to handle BOM
df_2019 = pd.read_csv('Files/PoPCites_Scopus_2019.csv', encoding='utf-8-sig')
df_2021 = pd.read_csv('Files/PoPCites_Scopus_2020.csv', encoding='utf-8-sig')
df_2021 = pd.read_csv('Files/PoPCites_Scopus_2021.csv', encoding='utf-8-sig')
df_2021 = pd.read_csv('Files/PoPCites_Scopus_2022.csv', encoding='utf-8-sig')
df_2021 = pd.read_csv('Files/PoPCites_Scopus_2023.csv', encoding='utf-8-sig')
df_2021 = pd.read_csv('Files/PoPCites_Scopus_2024.csv', encoding='utf-8-sig')

# Combine the DataFrames vertically
combined_df = pd.concat([df_2019, df_2021], ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('../Analysis/Combined_Scopus.csv', index=False, encoding='utf-8-sig')

print("Files combined successfully. Output saved to 'Combined_Scopus.csv'")