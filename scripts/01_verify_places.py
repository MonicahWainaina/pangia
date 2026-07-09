from pathlib import Path 
import pandas as pd 
# Locate the project root 
project_root = Path(__file__).resolve().parent.parent 
# Read the CSV 
csv_path = project_root / "data" / "master_places.csv" 
df = pd.read_csv(csv_path) 
print(df.head()) 
print() 
print(f"Total places: {len(df)}") 
