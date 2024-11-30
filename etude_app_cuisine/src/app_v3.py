import streamlit as st
import pandas as pd
import altair as alt
from models import IngredientMatcher
from models import SeasonalityChecker

# Chemin du dossier contenant les fichiers CSV


chemin = 'data/dico_all_month_ingredient'


# Chargement des données pour chaque mois
dico_all_month_ingredient = {}

for i in range(1, 13):
    # Lecture du CSV en gardant l'ordre d'origine
    dico_all_month_ingredient[i] = pd.read_csv(chemin + str(i) + '.csv')
    dico_all_month_ingredient[i].columns = ['ingredients', 'apparences', 'freq']


dico_all_month_ingredient_test={}


for i in range(1, 13):
    dico_all_month_ingredient_test[i]= dico_all_month_ingredient[i]
    dico_all_month_ingredient_test[i] = dico_all_month_ingredient_test[i].set_index('ingredients')
    dico_all_month_ingredient_test[i].index.name = None  

df_recipes_tokenised = pd.read_json("data/data_recipes_tokenised.json", orient="records")
df_recipes_tokenised['submitted'] = pd.to_datetime(df_recipes_tokenised['submitted'])

# Initialisation des classes 
matcher = IngredientMatcher(df_recipes_tokenised,dico_all_month_ingredient_test)
season_checker = SeasonalityChecker(dico_all_month_ingredient_test)







###### New Feature ########


thresold = 0.1#voir debug pour comprendre cette valeur


st.title("Analyse de la fréquence des ingrédients par mois")

# Sélection du mois avec un slider
selected_month = st.slider("Sélectionnez le mois", 1, 12)

# Entrer le nombre d'ingrédients à afficher
# Limiter l'entrée pour qu'elle soit entre 1 et la taille maximale de la liste d'ingrédients pour le mois sélectionné
max_ingredients = len(dico_all_month_ingredient[selected_month]) - 2
top = st.number_input("Nombre d'ingrédients à afficher", min_value=1, max_value=max_ingredients, value=20)

# Affichage de l'histogramme pour le mois sélectionné en conservant l'ordre des ingrédients
df_selected_month = dico_all_month_ingredient[selected_month]

df_selected_month['score']  =  df_selected_month.ingredients.apply(lambda x : matcher.ingredient_score(x))
df_selected_month = df_selected_month[df_selected_month.score > thresold]
df_selected_month = df_selected_month.iloc[2:top]


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







# Fonctionnalité sur les ingrédients choisis par l'utilisateur
st.title("Votre ingrédient est-il de saison ?")

user_ingredient = st.text_input("Entrez votre ingrédients :")


# Validation des données et bouton
if st.button("Vérifier meilleure saison"):
    if user_ingredient :
        try:
            # Conversion du mois en entier
            
            ingredient= str(user_ingredient.strip())
            # Appel de la fonction pour vérifier si l'ingrédient est de saison
            answer = season_checker.is_seasonal(ingredient)
            st.write(answer)
            # Affichage de la courbe d'apparition de l'ingrédient
            season_checker.plot_ingredient_frequency(ingredient)
            
        except ValueError:
            st.write("Veuillez entrer un mois valide (1-12).")
    else:
        st.write("Veuillez entrer un ingrédient et un mois pour continuer.")






### New feature ###







st.title("Vous ne savez pas quoi cuisiner ? Trouvons la meilleure recette de saison qui vous correspond !")

# Entrée utilisateur
user_seasonal_ingredient = st.text_input("Entrez votre ingrédient de saison :")
n_best_fit_ingredient = st.number_input("Combien d'autres ingrédients de saison voulez-vous ?", min_value=1, step=1)

# Conversion des entrées utilisateur

ingredient = str(user_seasonal_ingredient.strip())
N = int(n_best_fit_ingredient)


# Vérification si l'utilisateur a saisi un ingrédient
if user_seasonal_ingredient:
    # Recherche des ingrédients et des recettes
    seasonal_month = int(matcher.ingredient_best_seasonal(ingredient))

    result_N_match = matcher.seasonal_recommendations_1(ingredient, N)[1]
    result_recipes = matcher.seasonal_recommendations_1(ingredient, N)[0]
   
    st.subheader("Top ingredients match :")
    st.table(pd.DataFrame(result_N_match, columns=["Ingrédients"]))

    st.subheader("Top 10 Recettes recommandées :")
    st.write(df_recipes_tokenised.loc[result_recipes,'name'].reset_index(drop=True))
    
else:
        st.warning(f"L'ingrédient '{ingredient}' n'est pas trouvé dans les données pour la saison.")


