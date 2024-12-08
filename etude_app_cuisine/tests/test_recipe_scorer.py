import pytest
import numpy as np
import pandas as pd
from scipy.stats import norm
from models import RecipeScorer


@pytest.fixture
def df_recipes_stats():
    # Crée un DataFrame de test pour les recettes avec des notes et des
    # interactions
    data = {
        'recipe_id': [1, 2, 3, 4, 5],
        'nb_ratings': [10, 50, 5, 1, 100],
        'mean_rating': [4.5, 3.0, 5.0, 4.0, 2.0]
    }
    return pd.DataFrame(data)


@pytest.fixture
def scorer(df_recipes_stats):
    # Crée une instance de RecipeScorer avec les données de test
    return RecipeScorer(df_recipes_stats)


def test_reward_nb_ratings(scorer):
    # Test de la méthode reward_nb_ratings
    log_max = np.log(100)  # log du max des nb_ratings
    reward = scorer.reward_nb_ratings(10, log_max)
    expected_reward = (np.log(10) / log_max) * 5
    assert np.isclose(reward, expected_reward,
                      atol=1e-5), f"Expected {expected_reward}, but got {reward}"


def test_compute_score(scorer):
    # Test de la méthode compute_score
    poids_note = 0.6
    scores = scorer.compute_score(poids_note)
    assert len(scores) == 5, "Le nombre de scores calculés devrait être 5"
    assert all(
        scores >= 0) and all(
        scores <= 100), "Les scores doivent être entre 0 et 100"


def test_empirical_cdf(scorer):
    # Test de la méthode empirical_cdf
    data = np.array([1, 2, 3, 4, 5])
    sorted_data, cdf = scorer.empirical_cdf(data)
    expected_sorted_data = np.sort(data)
    expected_cdf = np.arange(1, len(data) + 1) / len(data)
    assert np.array_equal(
        sorted_data, expected_sorted_data), "Les données doivent être triées"
    assert np.allclose(
        cdf, expected_cdf, atol=1e-5), "La CDF empirique n'est pas correcte"


def test_objective(scorer):
    # Test de la méthode objective
    poids_note = 0.5
    mse = scorer.objective(poids_note)
    assert mse >= 0, "L'erreur quadratique moyenne doit être positive"


def test_optimize_weights(scorer):
    # Test de la méthode optimize_weights
    poids_note, poids_nb_reviews = scorer.optimize_weights()
    assert 0 <= poids_note <= 1, "Le poids des notes doit être entre 0 et 1"
    assert 0 <= poids_nb_reviews <= 1, "Le poids du nombre de reviews doit être entre 0 et 1"
    assert np.isclose(poids_note + poids_nb_reviews, 1.0,
                      atol=1e-5), "La somme des poids doit être égale à 1"
