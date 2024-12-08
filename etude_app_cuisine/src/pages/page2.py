import models
import streamlit as st
import pandas as pd
import altair as alt
import os
import sys
import importlib
from models import RecipeScorer

# Get the current directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

importlib.reload(models)

print(f"Debug: IngredientMatcher exists: {models.IngredientMatcher}")
print(f"Debug: SeasonalityChecker exists: {models.SeasonalityChecker}")
print(f"Debug: RecipeScorer exists: {models.RecipeScorer}")

# Path to the data_loaded folder
data_dir = os.path.join(parent_dir, "data_loaded")

# Paths to the CSV and JSON files
chemin = os.path.join(data_dir, 'dico_all_month_ingredient')
chemin_raw_interactions = os.path.join(data_dir, 'df_RAW_interactions.json')
chemin_raw_recipes = os.path.join(data_dir, 'df_RAW_recipes.json')
chemin_recipes_stats = os.path.join(data_dir, 'df_recipes_stats.json')
chemin_recipes_tokenised = os.path.join(data_dir, 'df_recipes_tokenised.json')

# Chargement des données pour chaque mois


@st.cache_data
def load_monthly_ingredient_data(chemin):
    dico_all_month_ingredient = {}
    for i in range(1, 13):
        # Lecture du CSV en gardant l'ordre d'origine
        df = pd.read_csv(f"{chemin}{i}.csv")
        df.columns = ['ingredients', 'apparences', 'freq']
        dico_all_month_ingredient[i] = df
    return dico_all_month_ingredient

# Préparation des données avec les ingrédients en index


@st.cache_data
def prepare_ingredient_data(dico_all_month_ingredient):
    dico_all_month_ingredient_test = {}
    for i in range(1, 13):
        df = dico_all_month_ingredient[i].copy()
        df.set_index('ingredients', inplace=True)
        df.index.name = None
        dico_all_month_ingredient_test[i] = df
    return dico_all_month_ingredient_test

# Charger les données des recettes tokenisées


@st.cache_data
def load_recipes_tokenised(chemin_recipes_tokenised):
    df = pd.read_json(chemin_recipes_tokenised, orient="records")
    df['submitted'] = pd.to_datetime(df['submitted'])
    return df

# Initialisation des classes


@st.cache_resource
def initialize_classes(df_recipes_tokenised, dico_all_month_ingredient_test):
    matcher = models.IngredientMatcher(
        df_recipes_tokenised,
        dico_all_month_ingredient_test)
    season_checker = models.SeasonalityChecker(dico_all_month_ingredient_test)
    return matcher, season_checker


# Charger et préparer les données
dico_all_month_ingredient = load_monthly_ingredient_data(chemin)
dico_all_month_ingredient_test = prepare_ingredient_data(
    dico_all_month_ingredient)
df_recipes_tokenised = load_recipes_tokenised(chemin_recipes_tokenised)

matcher, season_checker = initialize_classes(
    df_recipes_tokenised, dico_all_month_ingredient_test)

print(f"Debug: matcher instance created: {matcher}")
print(f"Debug: season_checker instance created: {season_checker}")

# Charger et indexer les données supplémentaires


@st.cache_data
def load_data(chemin_raw_recipes, chemin_raw_interactions,
              chemin_recipes_stats):
    df_RAW_recipes = pd.read_json(chemin_raw_recipes, lines=True)
    df_RAW_interactions = pd.read_json(chemin_raw_interactions, lines=True)
    df_recipes_stats = pd.read_json(chemin_recipes_stats, lines=True)
    return df_RAW_recipes, df_RAW_interactions, df_recipes_stats


@st.cache_data
def index_dataframes(df_recipes_stats, df_RAW_recipes):
    df_recipes_stats = df_recipes_stats.set_index('recipe_id')
    df_RAW_recipes = df_RAW_recipes.set_index('id')
    return df_recipes_stats, df_RAW_recipes


@st.cache_resource
def initialize_scorer(df_recipes_stats):
    return RecipeScorer(df_recipes_stats)


# Charger les données
df_RAW_recipes, df_RAW_interactions, df_recipes_stats = load_data(
    chemin_raw_recipes, chemin_raw_interactions, chemin_recipes_stats
)

# Indexer les DataFrames
df_recipes_stats, df_RAW_recipes = index_dataframes(
    df_recipes_stats, df_RAW_recipes)

# Initialisation de la classe RecipeScorer
scorer = initialize_scorer(df_recipes_stats)

# New Feature

threshold = 0.1  # Correction de l'orthographe de 'thresold' à 'threshold'

st.title("Analyse de la fréquence des ingrédients par mois")

# Sélection du mois avec un slider
selected_month = st.slider("Sélectionnez le mois", 1, 12)

# Entrer le nombre d'ingrédients à afficher
# Limiter l'entrée pour qu'elle soit entre 1 et la taille maximale de la
# liste d'ingrédients pour le mois sélectionné
# Assure que max_ingredients >=1
max_ingredients = max(len(dico_all_month_ingredient[selected_month]), 3) - 2
top = st.number_input(
    "Nombre d'ingrédients à afficher",
    min_value=1,
    max_value=max_ingredients,
    value=min(20, max_ingredients)
)

# Affichage de l'histogramme pour le mois sélectionné en conservant
# l'ordre des ingrédients
df_selected_month = dico_all_month_ingredient[selected_month].copy()

df_selected_month['score'] = df_selected_month['ingredients'].apply(
    matcher.ingredient_score)
df_selected_month = df_selected_month[df_selected_month['score'] > threshold]
df_selected_month = df_selected_month.iloc[:top]

# Création de l'histogramme avec Altair
chart = alt.Chart(df_selected_month).mark_bar().encode(
    # Conserve l'ordre d'origine des ingrédients
    x=alt.X('ingredients', sort=None),
    y='freq',
    tooltip=['ingredients', 'freq']
).properties(
    width=600,
    height=400,
    title=f"Fréquence des ingrédients pour le mois : {selected_month}"
)

# Affichage du graphique dans Streamlit
st.altair_chart(chart, use_container_width=True)

# New feature

st.title("Votre ingrédient est-il de saison ?")

user_ingredient = st.text_input(
    "Entrez votre ingrédient (en anglais) :",
    value="pumpkin")

# Validation des données et bouton
if st.button("Vérifier meilleure saison"):
    if user_ingredient:
        try:
            ingredient = user_ingredient.strip()
            # Appel de la fonction pour vérifier si l'ingrédient est de saison
            answer = season_checker.is_seasonal(ingredient)
            st.write(answer)
            # Affichage de la courbe d'apparition de l'ingrédient
            season_checker.plot_ingredient_frequency(ingredient)
        except Exception as e:
            st.write(f"Erreur: {e}")
    else:
        st.write("Veuillez entrer un ingrédient pour continuer.")

# New feature

st.title("Vous ne savez pas quoi cuisiner ? Trouvons la meilleure recette de saison qui vous correspond !")

# Entrée utilisateur
user_seasonal_ingredient = st.text_input(
    "Entrez votre ingrédient de saison (en anglais):",
    value="pumpkin")
n_best_fit_ingredient = st.number_input(
    "Combien d'autres ingrédients de saison voulez-vous ?",
    min_value=1,
    step=1,
    value=1
)

# Conversion des entrées utilisateur
ingredient = str(user_seasonal_ingredient.strip())
N = int(n_best_fit_ingredient)

# Fonction pour optimiser les poids et calculer les scores optimaux


@st.cache_data
def get_optimal_scores(_scorer, df_recipes_stats):
    """
    Optimise les poids et calcule les scores optimaux des recettes.

    Parameters:
    _scorer (RecipeScorer): Instance de RecipeScorer.
    df_recipes_stats (DataFrame): DataFrame contenant les statistiques des recettes.

    Returns:
    DataFrame: DataFrame avec une colonne 'optimal_score' ajoutée.
    """
    optimal_poids_note, optimal_poids_nb_reviews = _scorer.optimize_weights()
    df_stats = df_recipes_stats.copy()
    df_stats['optimal_score'] = _scorer.compute_score(optimal_poids_note)
    return df_stats

# Définition de la fonction pour afficher les recettes


def display_top_n_recipes(df_recipes_stats, df_RAW_recipes, df_RAW_interactions, n=5,
                          return_description=False, return_interactions=False, filter_recipe_names=None):
    """
    Affiche les n meilleures recettes selon le score optimal et renvoie les données associées.

    Parameters:
    df_recipes_stats (DataFrame): Le DataFrame contenant les statistiques des recettes.
    df_RAW_recipes (DataFrame): Le DataFrame contenant les données brutes des recettes.
    df_RAW_interactions (DataFrame): Le DataFrame contenant les interactions brutes des recettes.
    n (int): Le nombre de recettes à afficher. Par défaut, 5.
    return_description (bool): Si True, renvoie également la description des recettes. Par défaut, False.
    return_interactions (bool): Si True, renvoie également les interactions associées. Par défaut, False.
    filter_recipe_names (list): Une liste de noms de recettes à filtrer. Par défaut, None.

    Returns:
    None
    """
    # Filtrer les recettes par nom si filter_recipe_names est fourni
    if filter_recipe_names:
        filtered_ids = df_RAW_recipes[df_RAW_recipes['name'].isin(
            filter_recipe_names)].index
        df_recipes_stats_filtered = df_recipes_stats.loc[filtered_ids]
    else:
        df_recipes_stats_filtered = df_recipes_stats

    # Trouver les top_n recettes basées sur 'optimal_score'
    top_n_ids = df_recipes_stats_filtered.nlargest(n, 'optimal_score').index

    for i, recipe_id in enumerate(top_n_ids, start=1):
        st.write(f"#### Recette {i}")

        # Afficher les statistiques de la recette
        st.write("**Statistiques de la recette:**")
        st.write(df_recipes_stats.loc[recipe_id].to_frame().T)

        # Afficher la description de la recette
        if return_description:
            st.write("**Description de la recette:**")
            recipe_details = df_RAW_recipes.loc[recipe_id].copy()
            st.write(recipe_details.to_frame().T)

        # Afficher les interactions de la recette
        if return_interactions:
            st.write("**Interactions de la recette:**")
            interactions = df_RAW_interactions[df_RAW_interactions['recipe_id'] == recipe_id].copy(
            )
            interactions['date'] = pd.to_datetime(
                interactions['date']).dt.strftime('%Y-%m-%d')
            interactions = interactions.set_index(
                'recipe_id').sort_values(by='date', ascending=False)
            st.write(interactions)


# Vérification si l'utilisateur a saisi un ingrédient
if user_seasonal_ingredient:
    # Recherche des ingrédients et des recettes
    # seasonal_month = int(matcher.ingredient_best_seasonal(ingredient))

    result_N_match = matcher.seasonal_recommendations_1(ingredient, N)[1]
    result_recipes = matcher.seasonal_recommendations_1(ingredient, N)[0]

    st.subheader("Top ingrédients correspondants :")
    st.table(pd.DataFrame(result_N_match, columns=["Ingrédients"]))

    st.subheader("Recettes recommandées :")
    recommended_recipes = df_recipes_tokenised.loc[result_recipes, 'name'].reset_index(
        drop=True)
    st.write(recommended_recipes)

    # Optimiser les poids et calculer les scores optimaux avec cache
    df_recipes_stats_optimal = get_optimal_scores(scorer, df_recipes_stats)

    # Fonction de display
    st.subheader("Affichage des meilleures recettes selon leur score optimal")

    # Choix du nombre de recettes à afficher
    n = st.slider(
        "Nombre de recettes à afficher",
        min_value=1,
        max_value=10,
        value=3)

    # Choix de ce que l'utilisateur veut afficher
    return_description = st.checkbox(
        "Afficher la description des recettes", value=True)
    return_interactions = st.checkbox(
        "Afficher les interactions des recettes", value=False)

    # Filtrer les noms des recettes
    recipe_names = recommended_recipes.tolist()

    # Afficher les résultats
    display_top_n_recipes(
        df_recipes_stats_optimal,
        df_RAW_recipes,
        df_RAW_interactions,
        n=n,
        return_description=return_description,
        return_interactions=return_interactions,
        filter_recipe_names=recipe_names
    )

else:
    st.warning(
        "Veuillez entrer un ingrédient de saison pour obtenir des recommandations.")
