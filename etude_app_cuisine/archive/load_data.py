import pandas as pd
import ast
import os
from models import Preprocessing

# Chemin du dossier pour sauvegarder les fichiers CSV
save_path = 'etude_app_cuisine/src/data/'

# Assurez-vous que le répertoire de sauvegarde existe
os.makedirs(save_path, exist_ok=True)

# Charger le DataFrame brut (exemple fictif), préciser le chemin dans le README
df_RAW_recipes = pd.read_csv(
    '/Users/ramzi/Projet_Kit_Big_Data/data/RAW_recipes.csv')
df_pp_recipes = pd.read_csv(
    '/Users/ramzi/Projet_Kit_Big_Data/data/PP_recipes.csv')

# Nettoyer les données
df_RAW_recipes.submitted = pd.to_datetime(df_RAW_recipes.submitted)
df_RAW_recipes_merged = df_RAW_recipes.copy()
df_RAW_recipes_merged = df_RAW_recipes_merged.merge(
    df_pp_recipes, how='inner', on='id')
df_RAW_recipes_merged[df_RAW_recipes_merged.isna().any(
    axis=1)]  # Verification présence de NaN
df_RAW_recipes_merged.ingredients = df_RAW_recipes_merged.ingredients.apply(
    lambda x: ast.literal_eval(x))

# Instanciation de la classe Preprocessing
preprocessor = Preprocessing(df_RAW_recipes_merged)

# Dictionnaire des ingrédients par mois
dico_all_month_ingredient = {}

# Traitement pour chaque mois
for month in range(1, 13):
    # Création du dictionnaire pour chaque mois
    monthly_dico = preprocessor.create_monthly_dico_ingredient(month)
    counted_ingredients = preprocessor.count_ingredients(monthly_dico)
    lemmatized_and_sorted = preprocessor.lemmetize_and_sort(
        counted_ingredients)

    # Ajout au dictionnaire principal
    dico_all_month_ingredient[month] = lemmatized_and_sorted

    # Sauvegarde du DataFrame pour le mois en question en CSV
    lemmatized_and_sorted.to_csv(
        f'{save_path}/dico_all_month_ingredient{month}.csv')


print("Tous les fichiers CSV ont été sauvegardés avec succès.")

# Load mapping
mapping = preprocessor.mapping()
mapping.to_csv(f'{save_path}/mapping.csv')


# Load df_recipes_tokenised

df_recipes_tokenised = df_RAW_recipes_merged.copy()

df_recipes_tokenised.ingredients = df_recipes_tokenised.ingredients.apply(
    lambda x: preprocessor.tokenised_recipe(x, mapping))

df_recipes_tokenised['submitted'] = df_recipes_tokenised['submitted'].dt.strftime(
    '%Y-%m-%d')

df_recipes_tokenised.to_json(
    "tests/data/data_recipes_tokenised.json", orient="records", indent=4)
