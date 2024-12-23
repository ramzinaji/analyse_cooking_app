import pytest
import pandas as pd
import numpy as np
from models import SeasonalityChecker

# --- Configuration des données de test ---


@pytest.fixture
def dico_all_month_ingredient():
    """Fixture pour créer un dictionnaire simulé des ingrédients pour chaque mois."""
    data = {
        month: pd.DataFrame({
            'freq': [0, 10, 20, 30],
        }, index=['apple', 'banana', 'carrot', 'date'])
        for month in range(1, 13)
    }
    return data


@pytest.fixture
def checker(dico_all_month_ingredient):
    """Fixture pour initialiser l'objet SeasonalityChecker."""
    return SeasonalityChecker(dico_all_month_ingredient)

# --- Tests pour la méthode is_seasonal ---


def test_is_seasonal_good_choice(checker):
    """Test pour vérifier le meilleur mois d'un ingrédient."""
    result = checker.is_seasonal('carrot')
    assert result == "You should  cook carrot in January."


def test_is_seasonal_not_in_database(checker):
    """Test pour vérifier le comportement avec un ingrédient absent."""
    result = checker.is_seasonal('mango')
    assert result == "Your ingredient 'mango' is not in our database."

# --- Tests pour la méthode ingredient_std ---


def test_ingredient_std_normalized_values(checker):
    """Test pour vérifier la normalisation des valeurs et l'écart type."""
    norm_values, sigma_norm = checker.ingredient_std('carrot')
    assert isinstance(norm_values, np.ndarray)
    assert norm_values.shape == (12, 1)
    assert sigma_norm >= 0


def test_ingredient_std_not_in_database(checker):
    """Test pour vérifier le comportement avec un ingrédient absent."""
    result = checker.ingredient_std('mango')
    assert result == "Your ingredient 'mango' does not exist in the database."


def test_ingredient_std_error_handling(checker):
    """Test pour capturer une exception inattendue."""
    checker.dico_all_month_ingredient = None  # Provoquer une exception
    result = checker.ingredient_std('carrot')
    assert "An error occurred" in result
