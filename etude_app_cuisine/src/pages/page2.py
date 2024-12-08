import models
import streamlit as st
import pandas as pd
import altair as alt
import os
import sys
import importlib
import logging
from models import RecipeScorer

# -----------------------------------
# Logging Setup
# -----------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "streamlit_app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Log page initialization
logging.info("Page 2 loaded and logging initialized.")

# -----------------------------------
# File Paths Setup
# -----------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(script_dir)
sys.path.append(parent_dir)

data_dir = os.path.join(parent_dir, "data_loaded")
chemin = os.path.join(data_dir, 'dico_all_month_ingredient')
chemin_raw_interactions = os.path.join(data_dir, 'df_RAW_interactions.json')
chemin_raw_recipes = os.path.join(data_dir, 'df_RAW_recipes.json')
chemin_recipes_stats = os.path.join(data_dir, 'df_recipes_stats.json')
chemin_recipes_tokenised = os.path.join(data_dir, 'df_recipes_tokenised.json')

# Reload models
importlib.reload(models)
logging.info("Models reloaded successfully.")

# -----------------------------------
# Functions for Data Loading
# -----------------------------------
@st.cache_data
def load_monthly_ingredient_data(chemin):
    logging.info("Loading monthly ingredient data...")
    dico_all_month_ingredient = {}
    for i in range(1, 13):
        try:
            df = pd.read_csv(f"{chemin}{i}.csv")
            df.columns = ['ingredients', 'apparences', 'freq']
            dico_all_month_ingredient[i] = df
        except Exception as e:
            logging.error(f"Error loading month {i} data: {e}")
    logging.info("Monthly ingredient data loaded successfully.")
    return dico_all_month_ingredient

@st.cache_data
def prepare_ingredient_data(dico_all_month_ingredient):
    logging.info("Preparing ingredient data for indexing...")
    dico_all_month_ingredient_test = {}
    for i in range(1, 13):
        df = dico_all_month_ingredient[i].copy()
        df.set_index('ingredients', inplace=True)
        dico_all_month_ingredient_test[i] = df
    logging.info("Ingredient data preparation complete.")
    return dico_all_month_ingredient_test

@st.cache_data
def load_recipes_tokenised(chemin_recipes_tokenised):
    logging.info("Loading tokenized recipes...")
    try:
        df = pd.read_json(chemin_recipes_tokenised, orient="records")
        df['submitted'] = pd.to_datetime(df['submitted'])
        logging.info("Tokenized recipes loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"Failed to load tokenized recipes: {e}")
        return pd.DataFrame()

@st.cache_resource
def initialize_classes(df_recipes_tokenised, dico_all_month_ingredient_test):
    logging.info("Initializing IngredientMatcher and SeasonalityChecker...")
    try:
        matcher = models.IngredientMatcher(df_recipes_tokenised, dico_all_month_ingredient_test)
        season_checker = models.SeasonalityChecker(dico_all_month_ingredient_test)
        logging.info("Classes initialized successfully.")
        return matcher, season_checker
    except Exception as e:
        logging.error(f"Failed to initialize classes: {e}")
        return None, None

# -----------------------------------
# Data Loading and Initialization
# -----------------------------------
logging.info("Starting data loading process for Page 2...")
dico_all_month_ingredient = load_monthly_ingredient_data(chemin)
dico_all_month_ingredient_test = prepare_ingredient_data(dico_all_month_ingredient)
df_recipes_tokenised = load_recipes_tokenised(chemin_recipes_tokenised)
matcher, season_checker = initialize_classes(df_recipes_tokenised, dico_all_month_ingredient_test)

if matcher and season_checker:
    logging.info("Data loaded and models initialized successfully.")
else:
    logging.error("Failed to load data or initialize models.")

# -----------------------------------
# Streamlit Page Setup
# -----------------------------------
st.title("Analyse de la fréquence des ingrédients par mois")
logging.info("Rendered title for monthly ingredient analysis page.")

# Slider for Month Selection
selected_month = st.slider("Sélectionnez le mois", 1, 12)
logging.info(f"User selected month: {selected_month}")

# Number of Ingredients to Display
max_ingredients = max(len(dico_all_month_ingredient[selected_month]), 3) - 2
top = st.number_input(
    "Nombre d'ingrédients à afficher",
    min_value=1,
    max_value=max_ingredients,
    value=min(20, max_ingredients)
)
logging.info(f"User selected top {top} ingredients to display.")

# Histogram for Selected Month
try:
    df_selected_month = dico_all_month_ingredient[selected_month].copy()
    df_selected_month['score'] = df_selected_month['ingredients'].apply(matcher.ingredient_score)
    df_selected_month = df_selected_month[df_selected_month['score'] > 0.1].iloc[:top]

    chart = alt.Chart(df_selected_month).mark_bar().encode(
        x=alt.X('ingredients', sort=None),
        y='freq',
        tooltip=['ingredients', 'freq']
    ).properties(
        width=600,
        height=400,
        title=f"Fréquence des ingrédients pour le mois : {selected_month}"
    )
    st.altair_chart(chart, use_container_width=True)
    logging.info("Ingredient frequency chart rendered successfully.")
except Exception as e:
    logging.error(f"Failed to render ingredient chart: {e}")
    st.error("Erreur lors de l'affichage des données.")

# -----------------------------------
# Seasonality Checker Feature
# -----------------------------------
st.title("Votre ingrédient est-il de saison ?")
user_ingredient = st.text_input("Entrez votre ingrédient (en anglais) :", value="pumpkin")

if st.button("Vérifier meilleure saison"):
    logging.info(f"Checking seasonality for ingredient: {user_ingredient}")
    if user_ingredient:
        try:
            answer = season_checker.is_seasonal(user_ingredient.strip())
            st.write(answer)
            season_checker.plot_ingredient_frequency(user_ingredient.strip())
            logging.info(f"Displayed seasonality information for {user_ingredient}.")
        except Exception as e:
            logging.error(f"Error checking seasonality: {e}")
            st.error(f"Erreur: {e}")
    else:
        st.warning("Veuillez entrer un ingrédient pour continuer.")
        logging.warning("User did not input any ingredient.")

# -----------------------------------
# Recommendation Feature
# -----------------------------------
st.title("Vous ne savez pas quoi cuisiner ? Trouvons la meilleure recette de saison !")
user_seasonal_ingredient = st.text_input("Entrez votre ingrédient de saison (en anglais):", value="pumpkin")

if st.button("Lancer la recherche"):
    logging.info(f"Starting recommendation for ingredient: {user_seasonal_ingredient}")
    try:
        result_recipes = matcher.seasonal_recommendations_1(user_seasonal_ingredient, 5)[0]
        if result_recipes:
            st.subheader("Recettes recommandées :")
            st.write(df_recipes_tokenised.loc[result_recipes, 'name'])
            logging.info("Displayed recommended recipes.")
        else:
            st.warning("Aucune recette trouvée pour l'ingrédient donné.")
            logging.warning("No recipes found for user input.")
    except Exception as e:
        logging.error(f"Error fetching recommendations: {e}")
        st.error("Erreur lors de la recommandation des recettes.")
