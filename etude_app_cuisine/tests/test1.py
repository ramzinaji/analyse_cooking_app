import streamlit as st
import pandas as pd
import altair as alt
from utils import *

# Chemin du dossier contenant les fichiers CSV


chemin = '/Users/ramzi/Documents/Telecom_Master/Kit Big Data/projet_analyse_cuisine/etude_app_cuisine/tests/data/dico_all_month_ingredient'

# Chargement des données pour chaque mois
dico_all_month_ingredient = {}

for i in range(1, 13):
    # Lecture du CSV en gardant l'ordre d'origine
    dico_all_month_ingredient[i] = pd.read_csv(chemin + str(i) + '.csv')
    dico_all_month_ingredient[i].columns = ['ingredients', 'apparences', 'freq']

# Interface Streamlit
st.title("Analyse de la fréquence des ingrédients par mois")

# Sélection du mois avec un slider
selected_month = st.slider("Sélectionnez le mois", 1, 12)

# Entrer le nombre d'ingrédients à afficher
# Limiter l'entrée pour qu'elle soit entre 1 et la taille maximale de la liste d'ingrédients pour le mois sélectionné
max_ingredients = len(dico_all_month_ingredient[selected_month]) - 2
top = st.number_input("Nombre d'ingrédients à afficher", min_value=1, max_value=max_ingredients, value=20)

# Affichage de l'histogramme pour le mois sélectionné en conservant l'ordre des ingrédients
df_selected_month = dico_all_month_ingredient[selected_month].iloc[2:top]

# Création de l'histogramme avec Altair
chart = alt.Chart(df_selected_month).mark_bar().encode(
    x=alt.X('ingredients', sort=None),  # Conserve l'ordre d'origine des ingrédients
    y='freq',
    tooltip=['ingredients', 'freq']
).properties(
    width=600,
    height=400,
    title=f"Fréquence des ingrédients pour le mois : {selected_month}"
)

# Affichage du graphique dans Streamlit
st.altair_chart(chart, use_container_width=True)

### New feature ###
# Prétaitement (cette partie pourra être fonctionnalisé dans le fichier utils)
dico_all_month_ingredient_test={}
for i in range(1, 13):
    dico_all_month_ingredient_test[i]= dico_all_month_ingredient[i]
    dico_all_month_ingredient_test[i] = dico_all_month_ingredient_test[i].set_index('ingredients')
    dico_all_month_ingredient_test[i].index.name = None  

# Fonctionnalité sur les ingrédients choisis par l'utilisateur
st.title("Votre ingrédient est-il de saison ?")

user_ingredient = st.text_area("Entrez votre ingrédients :", height=5)
user_season = st.text_area("Entrez votre saison :", height=5)


# Validation des données et bouton
if st.button("Vérifier si de saison"):
    if user_ingredient and user_season:
        try:
            # Conversion du mois en entier
            month = int(user_season.strip())
            ingredient= str(user_ingredient.strip())
            # Appel de la fonction pour vérifier si l'ingrédient est de saison
            answer = is_seasonal(ingredient, month, dico_all_month_ingredient_test)
            st.write(answer)
        except ValueError:
            st.write("Veuillez entrer un mois valide (1-12).")
    else:
        st.write("Veuillez entrer un ingrédient et un mois pour continuer.")

