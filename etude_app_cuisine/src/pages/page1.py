import models
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import streamlit as st
from models import RecipeScorer
import os
import sys
import importlib
import logging

# -----------------------------------
# Logging Setup
# -----------------------------------
logging.info("Page 1: Initialization started.")

# Chemin des fichiers (adapter selon environnement)
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

# Ajouter les chemins nécessaires
sys.path.append(script_dir)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

importlib.reload(models)

# Log debugging information
logging.info(f"Debug: RecipeScorer exists: {models.RecipeScorer}")

data_dir = os.path.join(parent_dir, 'data_loaded')

# Chemin des fichiers JSON
chemin_raw_interactions = os.path.join(data_dir, 'df_RAW_interactions.json')
chemin_raw_recipes = os.path.join(data_dir, 'df_RAW_recipes.json')
chemin_recipes_stats = os.path.join(data_dir, 'df_recipes_stats.json')

# Log file paths
logging.info(f"Paths: {chemin_raw_interactions}, {chemin_raw_recipes}, {chemin_recipes_stats}")


@st.cache_data
def load_data():
    """Charge les données JSON nécessaires."""
    logging.info("Loading data...")
    try:
        df_RAW_recipes = pd.read_json(chemin_raw_recipes, lines=True)
        df_RAW_interactions = pd.read_json(chemin_raw_interactions, lines=True)
        df_recipes_stats = pd.read_json(chemin_recipes_stats, lines=True)
        logging.info("Data loaded successfully.")
        return df_RAW_recipes, df_RAW_interactions, df_recipes_stats
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        st.error("Error loading data. Please check file paths.")


@st.cache_data
def index_dataframes(df_recipes_stats, df_RAW_recipes):
    """Indexe les DataFrames pour des accès plus rapides."""
    logging.info("Indexing DataFrames...")
    df_recipes_stats = df_recipes_stats.set_index('recipe_id')
    df_RAW_recipes = df_RAW_recipes.set_index('id')
    logging.info("DataFrames indexed successfully.")
    return df_recipes_stats, df_RAW_recipes


@st.cache_resource
def initialize_scorer(df_recipes_stats):
    """Initialise l'objet RecipeScorer."""
    logging.info("Initializing RecipeScorer...")
    return RecipeScorer(df_recipes_stats)

###########################################
# INITIALISATION
###########################################

try:
    # Charger et indexer les données
    df_RAW_recipes, df_RAW_interactions, df_recipes_stats = load_data()
    df_recipes_stats, df_RAW_recipes = index_dataframes(
        df_recipes_stats, df_RAW_recipes)
    logging.info("Data loaded and indexed successfully.")
except Exception as e:
    logging.error(f"Initialization error: {e}")
    st.error("Error during data initialization.")

# Initialisation de la classe RecipeScorer
scorer = initialize_scorer(df_recipes_stats)

# Streamlit UI
st.title("Nouvelle méthode de scoring des recettes")
logging.info("Streamlit UI initialized.")

###########################################
# ETUDE DES NOTES MOYENNES
###########################################

try:
    st.subheader("1) Etude des notes moyennes des recettes")
    st.markdown("#### Histogramme des moyennes des notes")

    bins = st.slider(
        "Nombre de bins",
        min_value=10,
        max_value=50,
        value=20,
        step=5)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(
        df_recipes_stats['mean_rating'],
        bins=bins,
        edgecolor='black',
        alpha=0.7)
    ax.set_xlabel('Moyenne des notes')
    ax.set_ylabel('Fréquence')
    ax.set_title('Distribution des notes moyennes des recettes')
    plt.tight_layout()
    st.pyplot(fig)

    logging.info("Histogram of mean ratings displayed successfully.")
except Exception as e:
    logging.error(f"Error displaying histogram: {e}")
    st.error("Error displaying histogram of mean ratings.")

# 2) Diagramme circulaire
try:
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

    labels = []
    sizes = []
    for category, condition in categories.items():
        proportion = np.sum(condition) / len(mean_rating) * 100
        labels.append(f"{category}\n({proportion:.2f}%)")
        sizes.append(np.sum(condition))

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

    logging.info("Pie chart of mean ratings displayed successfully.")
except Exception as e:
    logging.error(f"Error displaying pie chart: {e}")
    st.error("Error displaying pie chart of mean ratings.")

# Additional sections
try:
    st.markdown("#### Fonction de répartition (CDF) des notes moyennes des recettes")
    sorted_scores, cdf = scorer.empirical_cdf(df_recipes_stats['mean_rating'])

    mu, std = stats.norm.fit(df_recipes_stats['mean_rating'])
    x = np.linspace(0, 5, 100)
    cdf_norm = stats.norm.cdf(x, mu, std)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        sorted_scores,
        cdf,
        marker='.',
        linestyle='none',
        label='CDF des scores')
    ax.plot(x, cdf_norm, 'r-', lw=2, label='CDF loi normale')
    ax.set_xlabel('Note')
    ax.set_ylabel('Fréquence cumulée')
    ax.set_title('CDF des notes moyennes des recettes vs. loi normale')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    st.write(f"Paramètres de la distribution normale ajustée: mu = {mu:.2f}, std = {std:.2f}")

    logging.info("CDF of mean ratings displayed successfully.")
except Exception as e:
    logging.error(f"Error displaying CDF: {e}")
    st.error("Error displaying CDF of mean ratings.")
