
import models
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import streamlit as st
from scipy.stats import norm
from scipy.optimize import minimize
from models import RecipeScorer
import os
import sys
import importlib


# Chemin des fichiers (adapter selon votre environnement)
# Get the current directory of the script
# Chemin du répertoire courant (page)
script_dir = os.path.dirname(__file__)

# Aller dans le répertoire parent (monter d'un niveau)
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

# Aller dans le répertoire "data" depuis le parent
sys.path.append(script_dir)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


importlib.reload(models)

print(f"Debug: RecipeScorer exists: {models.RecipeScorer}")


# Path to the data_loaded folder

data_dir = os.path.join(parent_dir, 'data_loaded')

# Chemin du dossier contenant les fichiers CSV
chemin_raw_interactions = os.path.join(data_dir, 'df_RAW_interactions.json')
chemin_raw_recipes = os.path.join(data_dir, 'df_RAW_recipes.json')
chemin_recipes_stats = os.path.join(data_dir, 'df_recipes_stats.json')

print(chemin_raw_interactions, chemin_raw_recipes, chemin_recipes_stats)


@st.cache_data
def index_dataframes(df_recipes_stats, df_RAW_recipes):
    df_recipes_stats = df_recipes_stats.set_index('recipe_id')
    df_RAW_recipes = df_RAW_recipes.set_index('id')
    return df_recipes_stats, df_RAW_recipes

###########################################
# INITIALISATION
###########################################


# Charger les données
df_RAW_recipes = pd.read_json(chemin_raw_recipes,  lines=True)
df_RAW_interactions = pd.read_json(chemin_raw_interactions,  lines=True)
df_recipes_stats = pd.read_json(chemin_recipes_stats,  lines=True)

# Indexer les DataFrames
df_recipes_stats, df_RAW_recipes = index_dataframes(
    df_recipes_stats, df_RAW_recipes)

# Initialisation de la classe RecipeScorer
scorer = RecipeScorer(df_recipes_stats)

# Streamlit UI
st.title("Nouvelle méthode de scoring des recettes")

###########################################
# ETUDE DES NOTES MOYENNES
###########################################

st.subheader("1) Etude des notes moyennes des recettes")

# 1) Histogramme de la distribution des moyennes des notes
st.markdown("#### Histogramme des moyennes des notes")
bins = st.slider("Nombre de bins", min_value=10,
                 max_value=50, value=20, step=5)
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df_recipes_stats['mean_rating'],
        bins=bins, edgecolor='black', alpha=0.7)
ax.set_xlabel('Moyenne des notes')
ax.set_ylabel('Fréquence')
ax.set_title('Distribution des notes moyennes des recettes')
plt.tight_layout()
st.pyplot(fig)

# 2) Diagramme circulaire
st.markdown("#### Diagramme circulaire des moyennes des notes")
mean_rating = df_recipes_stats['mean_rating']

# Définir les catégories
categories = {
    'notes <= 3': (mean_rating <= 3),
    '3 < notes < 4': (mean_rating > 3) & (mean_rating < 4),
    'notes = 4': mean_rating == 4,
    '4 < notes < 5': (mean_rating > 4) & (mean_rating < 5),
    'notes = 5': mean_rating == 5,
}

# Calculer les proportions
labels = []
sizes = []

for category, condition in categories.items():
    proportion = np.sum(condition) / len(mean_rating) * 100
    labels.append(f"{category}\n({proportion:.2f}%)")
    sizes.append(np.sum(condition))

# Tracer le camembert
fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=90,
    colors=plt.cm.tab10.colors,
    wedgeprops={'edgecolor': 'black'},
    pctdistance=0.85,
    labeldistance=1.1
)
plt.title('Répartition des notes moyennes des recettes', fontsize=14)
plt.tight_layout()
st.pyplot(fig)

# 3) CDF des moyennes des notes
st.markdown("#### Fonction de répartition (CDF) des notes moyennes des recettes")
sorted_scores, cdf = scorer.empirical_cdf(df_recipes_stats['mean_rating'])

# Loi normale
mu, std = stats.norm.fit(df_recipes_stats['mean_rating'])
x = np.linspace(0, 5, 100)
cdf_norm = stats.norm.cdf(x, mu, std)

# Graph
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sorted_scores, cdf, marker='.',
        linestyle='none', label='CDF des scores')
ax.plot(x, cdf_norm, 'r-', lw=2, label='CDF loi normale')
ax.set_xlabel('Note')
ax.set_ylabel('Fréquence cumulée')
ax.set_title('CDF des notes moyennes des recettes vs. loi normale')
ax.legend()
plt.tight_layout()
st.pyplot(fig)
st.write(
    f"Paramètres de la distribution normale ajustée: mu = {mu:.2f}, std = {std:.2f}")

###########################################
# ETUDE DU NOMBRE DE REVIEWS
###########################################

st.subheader("2) Etude du nombre de reviews des recettes")
st.markdown("#### Histogramme du nombre de reviews")
max_nb_ratings = st.slider(
    "Nombre max. de reviews par recette à afficher", 10, 100, 30)

# Histogramme de la distribution des avis
sub_nb_ratings = df_recipes_stats['nb_ratings'][df_recipes_stats['nb_ratings'] <= max_nb_ratings]

# Loi expo
loc, scale = stats.expon.fit(sub_nb_ratings, floc=0)
x = np.linspace(0, max_nb_ratings, 100)
pdf_expon = stats.expon.pdf(x, loc, scale)

# Graph
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(sub_nb_ratings, bins=range(0, max_nb_ratings + 2),
        edgecolor='black', align='left', density=True)
ax.plot(x, pdf_expon, 'r-', lw=2, label='PDF loi exponentielle')
ax.set_xlabel("Nombre de reviews par recette")
ax.set_ylabel("Fréquence")
ax.set_title(
    "Distribution du nombre de reviews par recette vs. loi exponentielle")
ax.legend()
ax.grid(True)
plt.tight_layout()
st.pyplot(fig)

# Afficher les paramètres de la distribution exponentielle ajustée
st.write(
    f"Paramètres de la distribution exponentielle ajustée: loc = {loc:.2f}, lambda = {1/scale:.2f}")

# CONCLUSION
st.subheader("3) Conclusion sur l'analyse des variables")
st.markdown("""
- **Variable 'Moyenne des notes des recettes'** : plus de 40% des notes moyennes sont égales à 5 --> la variable note ne permet pas de discriminer les recettes.
- **Variable 'Nombre de reviews des recettes'** : le nombre de reviews par recette décroît de façon quasi exponentielle --> bon facteur de discrimination.
""")

###########################################
# NOUVELLE METHODE DE SCORING
###########################################

# 1) Création du nouveau score
st.subheader("4) Nouvelle méthode de scoring basée sur la popularité")
st.markdown("""
- On décide de créer une nouvelle notation qui prend en compte à la fois les notes des utilisateurs et le nombre de reviews donné par recettes.  
- On transforme la variable "nombre de reviews" en note sur 5 grâce à une transformation logarithmique. Le logarithme réduit l'impact des valeurs extrêmes, évitant de survaloriser les recettes avec un très grand nombre de reviews par rapport à celles avec un nombre modéré.  
- Cette transformation reflète mieux notre jeu de données: une augmentation de 1 à 10 reviews est plus significative qu'une augmentation de 100 à 110.  
- Ce choix est pertinent car beaucoup de recettes ont seulement 1 avis, ce qui ne les récompense pas (log(1) = 0).  
- Chaque recette obtient deux notes attribuant des points entre 0 et 5. On effectue une moyenne pondérée de ces deux notes selon l’importance donnée à la note des utilisateurs.  
- Enfin, on rééchelonne cette note sur 100 pour obtenir une meilleure dispersion des notes.
- On cherche à obtenir un score dont la distribution suit une loi normale afin de garantir que la majorité des recettes ait des scores intermédiaires. De plus, en visant une distribution normale, on contraint les scores à mieux discriminer les recettes car les valeurs extrêmes sont en minorité.
""")

# Ajout d'un slider pour le poids des notes
poids_note = st.slider("Poids des notes", 0.0, 1.0, 0.4)
poids_nombre_reviews = 1 - poids_note
st.write(f"Poids du nombre de reviews: {poids_nombre_reviews:.2f}")

# Calcul des scores avec le poids actuel
df_recipes_stats['new_score'] = scorer.compute_score(poids_note)

# ------------------------------------
# 2) Visualisation
# ------------------------------------

# Histogramme du nouveau score
st.markdown("#### Histogramme du nouveau score des recettes")
fig, ax = plt.subplots(figsize=(10, 6))
mu, std = stats.norm.fit(df_recipes_stats['new_score'])
x = np.linspace(0, 100, 100)
pdf_norm = stats.norm.pdf(x, mu, std)
ax.hist(df_recipes_stats['new_score'], bins=20,
        density=True, edgecolor='black', alpha=0.6)
ax.plot(x, pdf_norm, 'r-', lw=2, label='PDF loi normale')
ax.set_xlabel("Nouveau score")
ax.set_ylabel("Densité")
ax.set_title("Distribution du nouveau score des recettes vs. loi normale")
plt.legend()
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)

# CDF des scores
st.markdown("#### Fonction de répartition (CDF) des nouveaux scores des recettes")
sorted_scores, cdf = scorer.empirical_cdf(df_recipes_stats['new_score'])
cdf_norm = stats.norm.cdf(x, mu, std)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sorted_scores, cdf, marker='.',
        linestyle='none', label='CDF nouveaux scores')
ax.plot(x, cdf_norm, 'r-', lw=2, label='CDF loi normale')
ax.set_xlabel("Nouveau score")
ax.set_ylabel("Fréquence cumulée")
ax.set_title("CDF des nouveaux scores vs. loi normale")
plt.legend()
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)
st.write(
    f"Paramètres de la distribution normale ajustée: μ = {mu:.2f}, σ = {std:.2f}")

# Calcul du MSE actuel
mse_current = scorer.objective(poids_note)
st.write(
    f"Erreur quadratique moyenne (MSE) avec la loi normale : {mse_current:.5f}")

###########################################
# RECHERCHE DES POIDS OPTIMAUX
###########################################

st.subheader("5) Recherche des poids optimaux")
st.markdown("""
On a cherché à déterminer avec précision les paramètres de poids permettant d'obtenir une variable de scoring dont la distribution soit la plus proche possible d'une loi normale.
Pour cela, nous avons minimisé une fonction de coût définie comme la somme des écarts quadratiques entre la fonction de répartition (CDF) de notre feature et celle de la loi normale associée.
Les résultats sont présentés ci-dessous.
""")

# Optimisation des poids
optimal_poids_note, optimal_poids_nb_reviews = scorer.optimize_weights()

# Affichage des poids optimaux
st.markdown("#### Poids optimaux")
st.write(f"Poids des notes : {optimal_poids_note:.2f}")
st.write(f"Poids du nombre de reviews : {optimal_poids_nb_reviews:.2f}")

# MSE pour les scores optimaux
mse_optimal = scorer.objective(optimal_poids_note)
st.write(
    f"Erreur quadratique moyenne (MSE) pour les scores optimaux : {mse_optimal:.5f}")

# Calcul des scores avec les poids optimaux
df_recipes_stats['optimal_score'] = scorer.compute_score(optimal_poids_note)

# Histogramme des nouveaux scores optimaux
st.markdown("#### Histogramme des scores optimaux des recettes")
fig, ax = plt.subplots(figsize=(10, 6))
mu_opt, std_opt = stats.norm.fit(df_recipes_stats['optimal_score'])
x = np.linspace(0, 100, 100)
pdf_norm_opt = stats.norm.pdf(x, mu_opt, std_opt)
ax.hist(df_recipes_stats['optimal_score'], bins=20,
        density=True, edgecolor='black', alpha=0.6)
ax.plot(x, pdf_norm_opt, 'r-', lw=2, label='PDF loi normale')
ax.set_xlabel("Score optimal")
ax.set_ylabel("Densité")
ax.set_title("Distribution des scores optimaux vs. loi normale")
plt.legend()
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)

# CDF des scores optimaux
st.markdown("#### Fonction de répartition (CDF) des scores optimaux des recettes")
sorted_scores_opt, cdf_opt = scorer.empirical_cdf(
    df_recipes_stats['optimal_score'])
cdf_norm_opt = stats.norm.cdf(x, mu_opt, std_opt)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sorted_scores_opt, cdf_opt, marker='.',
        linestyle='none', label='CDF scores optimaux')
ax.plot(x, cdf_norm_opt, 'r-', lw=2, label='CDF loi normale')
ax.set_xlabel("Score optimal")
ax.set_ylabel("Fréquence cumulée")
ax.set_title("CDF des scores optimaux vs. loi normale")
plt.legend()
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)

# CONCLUSION
st.subheader("6) Conclusion sur la nouvelle méthode de scoring")
st.markdown("""
- On est parvenu à créer une nouvelle feature permettant de mieux évaluer les recettes en prenant en compte à la fois la qualité perçue par les utilisateurs (la  note) et la popularité auprès de ces derniers (le nombre de reviews).  
- Le nouveau score permet de mieux discriminer les recettes grâce à une distribution proche d'une loi normale.
- Il reste tout de même certaines recettes qu'on ne parvient pas à discriminer, notamment celles avec une seule review et une note moyenne égale à 5 (donc une seule note égale à 5).
""")

# AFFICHAGE DU TOP N

# Fonction affichant les meilleures recettes selon le score optimal


def display_top_n_recipes(df_recipes_stats, df_RAW_recipes, df_RAW_interactions, n=5, return_description=False, return_interactions=False):
    """
    Affiche les n meilleures recettes selon le score optimal et renvoie les données associées.

    Parameters:
    df_recipes_stats (DataFrame): Le DataFrame contenant les statistiques des recettes.
    df_RAW_recipes (DataFrame): Le DataFrame contenant les données brutes des recettes.
    df_RAW_interactions (DataFrame): Le DataFrame contenant les interactions brutes des recettes.
    n (int): Le nombre de recettes à afficher. Par défaut, 10.
    return_description (bool): Si True, renvoie également la description des recettes. Par défaut, False.
    return_interactions (bool): Si True, renvoie également les interactions associées. Par défaut, False.

    Returns:
    list: Une liste de DataFrames contenant les statistiques des recettes, les descriptions et les interactions associées.
    """

    # Trouver les top_n recettes basées sur 'optimal_score'
    top_n_ids = df_recipes_stats.nlargest(n, 'optimal_score').index

    # Initialiser les résultats à renvoyer
    results = []

    for i, recipe_id in enumerate(top_n_ids, start=1):
        st.write(f"#### Recette {i}")

        # Ajouter les statistiques associées
        st.write("Statistiques de la recette:")
        st.write(df_recipes_stats.loc[recipe_id].to_frame().T)

        # Ajouter la description de la recette
        if return_description:
            st.write("Description de la recette:")
            # Convertir 'submitted' en format YYYY-MM-DD
            df_RAW_recipes.loc[recipe_id, 'submitted'] = pd.to_datetime(
                df_RAW_recipes.loc[recipe_id, 'submitted']).strftime('%Y-%m-%d')
            st.write(df_RAW_recipes.loc[recipe_id].to_frame().T)

        # Ajouter les interactions associées
        if return_interactions:
            st.write("Interactions de la recette:")
            interactions = df_RAW_interactions[df_RAW_interactions['recipe_id'] == recipe_id]
            # Convertir 'date' en format YYYY-MM-DD
            interactions['date'] = pd.to_datetime(
                interactions['date']).dt.strftime('%Y-%m-%d')
            interactions = interactions.set_index('recipe_id')
            interactions = interactions.sort_values(by='date', ascending=False)
            st.write(interactions)

    return results


# Exemple d'utilisation de la fonction
st.subheader("7) Affichage des meilleures recettes selon leur score optimal")

# Choix du nombre de recettes à afficher
n = st.slider("Nombre de recettes à afficher",
              min_value=1, max_value=10, value=5)

# Choix de ce que l'utilisateur veut afficher
return_description = st.checkbox(
    "Afficher la description des recettes", value=True)
return_interactions = st.checkbox(
    "Afficher les interactions des recettes", value=False)

# Afficher les résultats
display_top_n_recipes(df_recipes_stats, df_RAW_recipes, df_RAW_interactions, n=n,
                      return_description=return_description, return_interactions=return_interactions)
