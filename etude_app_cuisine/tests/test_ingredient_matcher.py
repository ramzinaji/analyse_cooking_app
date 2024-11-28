import pytest
from models import IngredientMatcher  
import pandas as pd


@pytest.fixture
def tokenized_data():
    data = {
        "submitted": pd.to_datetime(["2020-01-01", "2020-02-01"]),
        "ingredients": [["tomato", "onion"], ["carrot", "tomato"]],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_dico():
    return {
        month: pd.DataFrame({
            "ingredient": ["tomato", "onion"],
            "freq": [10 * month, 5 * month],
        }).set_index("ingredient") for month in range(1, 13)
    }


@pytest.fixture
def ingredient_matcher(tokenized_data, mock_dico):
    return IngredientMatcher(tokenized_data, mock_dico)


def test_ingredient_match(ingredient_matcher):
    result = ingredient_matcher.ingredient_match("tomato", 1)
    assert "onion" in result
    assert result["tomato"] == 2


def test_check_elements_in_list(ingredient_matcher):
    assert ingredient_matcher.check_elements_in_list(["tomato"], ["tomato", "onion"]) is True
    assert ingredient_matcher.check_elements_in_list(["pepper"], ["tomato", "onion"]) is False


def test_recipes_filter_by_ingredients(ingredient_matcher):
    result = ingredient_matcher.recipes_filter_by_ingredients(["tomato"], 1)
    assert len(result) == 1
