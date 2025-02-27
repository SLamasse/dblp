import os
import pandas as pd
import matplotlib.pyplot as plt

# Répertoire contenant les fichiers CSV
results_dir = "results"

# Vérifier si le répertoire existe
if not os.path.exists(results_dir):
    raise FileNotFoundError(f"Le répertoire '{results_dir}' n'existe pas.")

# Fichier de sortie combiné
output_file = "combined.csv"

# Ouvrir le fichier de sortie en mode écriture
with open(output_file, 'w', encoding='utf-8') as outfile:
    # Écrire l'en-tête une seule fois
    header_written = False

    # Parcourir tous les fichiers dans le répertoire "results"
    for filename in os.listdir(results_dir):
        if filename.endswith("_parsed_data.csv"):  # Ne prendre que les fichiers de données parsées
            filepath = os.path.join(results_dir, filename)
            try:
                # Lire le fichier CSV
                df = pd.read_csv(filepath, sep=';')

                # Écrire l'en-tête uniquement pour le premier fichier
                if not header_written:
                    df.to_csv(outfile, sep=';', index=False, mode='w')
                    header_written = True
                else:
                    # Écrire les données sans l'en-tête
                    df.to_csv(outfile, sep=';', index=False, mode='a', header=False)
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {filename}: {e}")

# Lire le fichier combiné
combined_df = pd.read_csv(output_file, sep=';')

# Vérifier si la colonne des années existe
if combined_df.shape[1] < 3:
    raise ValueError("Le fichier CSV ne contient pas suffisamment de colonnes. Assurez-vous que la colonne des années est présente.")

# Extraire la colonne des années (3ème colonne, index 2)
years = combined_df.iloc[:, 2]

# Convertir les années en nombres (au cas où elles sont stockées sous forme de chaînes)
try:
    years = pd.to_numeric(years, errors='coerce')  # Convertir en nombres, remplacer les erreurs par NaN
except ValueError as e:
    raise ValueError(f"Erreur lors de la conversion des années en nombres : {e}")

# Supprimer les lignes où l'année est NaN
years_cleaned = years.dropna()

# Vérifier si des données valides restent
if years_cleaned.empty:
    raise ValueError("Aucune année valide trouvée dans les données.")

# Convertir les années en entiers
years_cleaned = years_cleaned.astype(int)

# Créer l'histogramme
theme = "'handwritten'"

plt.figure(figsize=(10, 6))
plt.hist(years_cleaned, bins=range(min(years_cleaned), max(years_cleaned) + 1), edgecolor='black', align='left')
plt.xlabel("Années")
plt.ylabel("Nombre de publications")
plt.title(f"Publications référencées dans DBLP portant sur {theme} par année")
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.xticks(range(min(years_cleaned), max(years_cleaned) + 1), rotation=45)  # Afficher toutes les années
plt.tight_layout()  # Ajuster la mise en page
plt.show()

# Supprimer le fichier combiné après utilisation (optionnel)
os.remove(output_file)
