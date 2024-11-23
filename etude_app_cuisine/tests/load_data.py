import pandas as pd
import os

# Assurez-vous que la classe Preprocessing et les autres nécessaires sont importées
from models import Preprocessing  # Importer la classe Preprocessing

# Chemin du dossier pour sauvegarder les fichiers CSV
save_path = '/Users/ramzi/Documents/Telecom_Master/Kit Big Data/projet_analyse_cuisine/etude_app_cuisine/tests/data'

# Assurez-vous que le répertoire de sauvegarde existe
os.makedirs(save_path, exist_ok=True)

# Charger le DataFrame brut (exemple fictif)
df_RAW_recipes_merged = pd.read_csv('/Users/ramzi/Projet_Kit_Big_Data/data/RAW_recipes.csv')

# Instanciation de la classe Preprocessing
preprocessor = Preprocessing(df_RAW_recipes_merged)

# Dictionnaire des ingrédients par mois
dico_all_month_ingredient = {}

# Traitement pour chaque mois
for month in range(1, 13):
    # Création du dictionnaire pour chaque mois
    monthly_dico = preprocessor.create_monthly_dico_ingredient(month)
    counted_ingredients = preprocessor.count_ingredients(monthly_dico)
    lemmatized_and_sorted = preprocessor.lemmetize_and_sort(counted_ingredients)
    
    # Ajout au dictionnaire principal
    dico_all_month_ingredient[month] = lemmatized_and_sorted

    # Sauvegarde du DataFrame pour le mois en question en CSV
    lemmatized_and_sorted.to_csv(f'{save_path}/dico_all_month_ingredient_{month}.csv')

print("Tous les fichiers CSV ont été sauvegardés avec succès.")
