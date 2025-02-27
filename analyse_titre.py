import os
import pandas as pd
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk

# Télécharger les stopwords de NLTK (si ce n'est pas déjà fait)
nltk.download('stopwords')

# Configuration
RESULTS_DIR = "results"
OUTPUT_FILE = "combined.csv"
STOPWORDS = set(stopwords.words('english'))

def check_directory_exists(directory):
    """Vérifie si un répertoire existe."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Le répertoire '{directory}' n'existe pas.")

def combine_csv_files(results_dir, output_file):
    """Combine tous les fichiers CSV d'un répertoire en un seul fichier."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        header_written = False
        for filename in os.listdir(results_dir):
            if filename.endswith("_parsed_data.csv"):
                filepath = os.path.join(results_dir, filename)
                try:
                    df = pd.read_csv(filepath, sep=';')
                    if not header_written:
                        df.to_csv(outfile, sep=';', index=False, mode='w')
                        header_written = True
                    else:
                        df.to_csv(outfile, sep=';', index=False, mode='a', header=False)
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {filename}: {e}")

def preprocess_text(text):
    """Prétraitement du texte : conversion en minuscules, suppression de la ponctuation, tokenisation, suppression des stopwords."""
    text = text.lower()
    text = ''.join([char for char in text if char.isalnum() or char == ' '])
    tokens = text.split()
    tokens = [word for word in tokens if word not in STOPWORDS]
    return tokens

def analyze_word_frequency(df):
    """Analyse la fréquence des mots dans les titres."""
    df['tokens'] = df['title'].apply(preprocess_text)
    all_tokens = [word for tokens in df['tokens'] for word in tokens]
    word_freq = Counter(all_tokens)
    return word_freq

def plot_word_cloud(word_freq):
    """Affiche un nuage de mots à partir des fréquences des mots."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Nuage de mots des titres (sans stopwords)")
    plt.show()

def plot_top_words(word_freq, top_n=20):
    """Affiche un histogramme des mots les plus fréquents."""
    top_words = word_freq.most_common(top_n)
    words, frequencies = zip(*top_words)
    plt.figure(figsize=(10, 5))
    plt.bar(words, frequencies, color='skyblue')
    plt.xlabel("Mots")
    plt.ylabel("Fréquence")
    plt.title(f"{top_n} mots les plus fréquents dans les titres (sans stopwords)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def analyze_trends_by_year(df, word):
    """Analyse l'évolution d'un mot-clé dans les titres au fil des années."""
    df['contains_word'] = df['title'].str.contains(word, case=False, na=False)
    trends = df.groupby('year')['contains_word'].sum()
    return trends

def plot_word_trends(df, top_n=15):
    """Affiche l'évolution des mots les plus fréquents au fil des années."""
    word_freq = analyze_word_frequency(df)
    top_words = word_freq.most_common(top_n)
    fig, axes = plt.subplots(5, 3, figsize=(18, 20))
    fig.suptitle(f"Évolution des {top_n} mots les plus fréquents dans les titres", fontsize=16)
    for i, (word, _) in enumerate(top_words):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        trends = analyze_trends_by_year(df, word)
        trends.plot(kind='line', marker='o', color='orange', ax=ax)
        ax.set_title(f"Évolution du mot '{word}'")
        ax.set_xlabel("Années")
        ax.set_ylabel("Nombre de publications")
        ax.grid(True)
    plt.tight_layout()
    plt.show()

def build_frequency_by_date(df):
    """Construit un DataFrame de fréquence des mots par date."""
    freq_dict = defaultdict(lambda: defaultdict(int))
    for _, row in df.iterrows():
        year = row['year']
        tokens = row['tokens']
        for word in tokens:
            freq_dict[word][year] += 1
    freq_df = pd.DataFrame.from_dict(freq_dict, orient='index').fillna(0)
    freq_df = freq_df[sorted(freq_df.columns)]
    return freq_df
def plot_word_trends_comparison(df, words, normalize=False):
    """
    Affiche un graphique comparant l'évolution de plusieurs mots-clés au fil des années.

    Args:
        df (pd.DataFrame): Le DataFrame contenant les colonnes 'title' et 'year'.
        words (list): Une liste de mots-clés à comparer.
        normalize (bool): Si True, affiche les fréquences relatives. Sinon, affiche les valeurs absolues.
    """
    plt.figure(figsize=(12, 6))

    for word in words:
        trends = analyze_trends_by_year(df, word)
        if normalize:
            total_count = trends.sum()
            trends = trends / total_count * 100  # Convertir en pourcentage
        trends.plot(kind='line', marker='o', label=word)

    plt.xlabel("Années")
    plt.ylabel("Nombre de publications" if not normalize else "Fréquence relative (%)")
    plt.title("Évolution comparée des mots-clés dans les titres")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    check_directory_exists(RESULTS_DIR)
    combine_csv_files(RESULTS_DIR, OUTPUT_FILE)
    combined_df = pd.read_csv(OUTPUT_FILE, sep=';', names=['id', 'title', 'year', 'publication', 'pages', 'doi'])

    if 'title' not in combined_df.columns:
        raise ValueError("La colonne 'title' est manquante dans les données.")

    word_freq = analyze_word_frequency(combined_df)
    print("20 mots les plus fréquents :")
    for word, freq in word_freq.most_common(20):
        print(f"{word}: {freq}")

    plot_word_cloud(word_freq)
    plot_top_words(word_freq)
    plot_word_trends(combined_df)

    freq_by_date_df = build_frequency_by_date(combined_df)
    freq_by_date_df.to_csv('tfg.csv', sep=';')
    print("Le fichier 'tfg.csv' a été créé avec succès.")

    words_to_compare = ["intelligence", "machine", "learning", "data", "network"]
    plot_word_trends_comparison(combined_df, words_to_compare, normalize=True)

    os.remove(OUTPUT_FILE)

if __name__ == "__main__":
    main()

