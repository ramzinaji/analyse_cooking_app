import streamlit as st
import pandas as pd
import altair as alt

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
