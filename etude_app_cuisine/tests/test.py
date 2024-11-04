import streamlit as st
import pandas as pd

chemin ='/Users/ramzi/Documents/Telecom_Master/Kit Big Data/projet_analyse_cuisine/etude_app_cuisine/dico_all_month_ingredient'

dico_all_month_ingredient={}

for i in range(1,13):   
    dico_all_month_ingredient[i]=pd.read_csv(chemin + str(i) +'.csv')
    dico_all_month_ingredient[i].columns=['ingredients','apparences','freq']

        
    
# Interface Streamlit
st.title("Analyse de la fréquence des ingrédients par mois")

# Sélection du mois avec un slider
selected_month = st.slider("Sélectionnez le mois", 1, 12)

# Affichage de l'histogramme pour le mois sélectionné
top = 20
st.write(f"Fréquence des ingrédients pour le mois : {selected_month}")
st.bar_chart(dico_all_month_ingredient[selected_month].iloc[2:top], x='ingredients' ,y="freq")