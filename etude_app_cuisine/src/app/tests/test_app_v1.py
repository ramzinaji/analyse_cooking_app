"""Test the app_v1.py file."""
import pandas as pd
from streamlit.testing.v1 import AppTest

def test_app_v1():
    """Test the app with mocked data."""
    # Mock data for testing
    mock_data = {
        "ingredients": ["pepper", "salt", "sugar", "onion", "oil"],
        "apparences": [7578.0, 6227.0, 5546.0, 5125.0, 5108.0],
        "freq": [52.71, 43.31, 38.57, 35.64, 35.53],
    }
    mock_df = pd.DataFrame(mock_data).set_index("ingredients")

    app = AppTest.from_file("app_v1.py").run()

        # Test the slider interaction
    assert app.slider[0].value == 1
    app.slider[0].set_value(3).run()
    assert app.slider[0].value == 3

        # Test the number input interaction
    max_ingredients = len(mock_df) - 2
    app.number_input[0].set_value(max_ingredients).run()
    assert app.number_input[0].value == max_ingredients

        # Test with different slider value
    app.slider[0].set_value(5).run()
    assert app.slider[0].value == 5

        # Test with different number input value
    app.number_input[0].set_value(3).run()
    assert app.number_input[0].value == 3

        # Test with different text areas for ingredient and month
    app.text_area[0].set_value("salt").run()
    app.text_area[1].set_value("10").run()
    app.button[0].click().run()
    assertion = app.markdown[0].value
    assert "Good choice,the best season to cook " in assertion

        # Test with invalid month
    app.text_area[1].set_value("13").run()
    app.button[0].click().run()
    assertion = app.markdown[0].value
    assert "Veuillez entrer un mois valide (1-12)." in assertion

        # Test with empty ingredient
    app.text_area[0].set_value("").run()
    app.button[0].click().run()
    assertion = app.markdown[0].value
    assert "Veuillez entrer un ingrédient et un mois pour continuer." in assertion
