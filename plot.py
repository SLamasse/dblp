import numpy as np 
import matplotlib.pyplot as plt  
import pandas as pd




filename = "parsed_data.csv"
df = pd.read_csv(filename,  sep =';')
data = pd.Series(df.iloc[:,2])
plt.(data, bins=100)
plt.xlabel("Annees")
plt.ylabel("Fréquences")
plt.title("Publications portant sur l'IA")
plt.show()

