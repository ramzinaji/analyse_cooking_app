import sys
sys.path.append('C:/Users/nawfal/Documents/telecom/periode1/kit_big_data/project/analyse_cooking_app/etude_app_cuisine/app')

import os
from unittest.mock import patch
import pandas as pd
import altair as alt

# Add the path to the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Mock the pandas read_csv function to avoid FileNotFoundError
@patch('pandas.read_csv')
@patch('streamlit.slider')
@patch('streamlit.number_input')
@patch('streamlit.text_area')
@patch('streamlit.button')
@patch('streamlit.write')
@patch('streamlit.altair_chart')
@patch('streamlit.title')


def test_streamlit_app(mock_title, mock_altair_chart, mock_write, mock_button, mock_text_area, mock_number_input, mock_slider, mock_read_csv):
    # Mocking the read_csv function to return a predefined DataFrame
    mock_read_csv.return_value = pd.DataFrame({
        'ingredients': ['Tomato', 'Potato'],
        'apparences': [10, 20],
        'freq': [0.5, 0.8]
    })

    # Import the is_seasonal function after mocking read_csv
    from app.app_v1 import is_seasonal

    # Mocking Streamlit components
    mock_title.side_effect = ["Analyse de la fréquence des ingrédients par mois", "Votre ingrédient est-il de saison ?"]
    mock_slider.return_value = 5
    mock_number_input.return_value = 10
    mock_text_area.side_effect = ["Tomato", "5"]
    mock_button.side_effect = [False, True]

    # Mocking the data
    dico_all_month_ingredient = {
        5: pd.DataFrame({
            'ingredients': ['Tomato', 'Potato'],
            'apparences': [10, 20],
            'freq': [0.5, 0.8]
        })
    }

    # Simulate the Streamlit app execution
    selected_month = mock_slider("Sélectionnez le mois", 1, 12)
    max_ingredients = len(dico_all_month_ingredient[selected_month]) - 2
    top = mock_number_input("Nombre d'ingrédients à afficher", min_value=1, max_value=max_ingredients, value=20)
    df_selected_month = dico_all_month_ingredient[selected_month].iloc[2:top]
    chart = alt.Chart(df_selected_month).mark_bar().encode(
        x=alt.X('ingredients', sort=None),
        y='freq',
        tooltip=['ingredients', 'freq']
    ).properties(
        width=600,
        height=400,
        title=f"Fréquence des ingrédients pour le mois : {selected_month}"
    )
    mock_altair_chart(chart, use_container_width=True)

    # Check the first button interaction (should not call write)
    if mock_button("Vérifier si de saison"):
        user_ingredient = mock_text_area("Entrez votre ingrédients :", height=5)
        user_season = mock_text_area("Entrez votre saison :", height=5)
        if user_ingredient and user_season:
            try:
                month = int(user_season.strip())
                ingredient = str(user_ingredient.strip())
                answer = is_seasonal(ingredient, month, dico_all_month_ingredient)
                mock_write(answer)
            except ValueError:
                mock_write("Veuillez entrer un mois valide (1-12).")
        else:
            mock_write("Veuillez entrer un ingrédient et un mois pour continuer.")

    # Verify the calls
    mock_title.assert_any_call("Analyse de la fréquence des ingrédients par mois")
    mock_title.assert_any_call("Votre ingrédient est-il de saison ?")
    mock_slider.assert_called_once_with("Sélectionnez le mois", 1, 12)