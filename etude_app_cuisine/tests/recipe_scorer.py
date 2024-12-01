import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize

class RecipeScorer:
    def __init__(self, df_recipes_stats):
        """
        Initialise la classe RecipeScorer avec les statistiques des recettes.

        Parameters:
        df_recipes_stats (DataFrame): Le DataFrame contenant les statistiques des recettes.
        """
        self.df_recipes_stats = df_recipes_stats

    def reward_nb_ratings(self, nb_ratings, log_max):
        """
        Calcule une récompense pour le nombre de notes en utilisant une transformation logarithmique.

        Parameters:
        nb_ratings (int): Le nombre de notes pour une recette.
        log_max (float): Le logarithme du nombre maximum de notes.

        Returns:
        float: La récompense calculée pour le nombre de notes.
        """
        return (np.log(nb_ratings) / log_max) * 5

    def compute_score(self, poids_note):
        """
        Calcule le score pondéré pour chaque recette en fonction des notes moyennes et du nombre de notes.

        Parameters:
        poids_note (float): Le poids attribué aux notes moyennes.

        Returns:
        Series: Les nouveaux scores calculés pour chaque recette.
        """
        log_max = np.log(max(self.df_recipes_stats['nb_ratings']))
        poids_nb_reviews = 1 - poids_note
        self.df_recipes_stats['rewarded_nb_ratings'] = self.df_recipes_stats['nb_ratings'].apply(self.reward_nb_ratings, log_max=log_max)
        self.df_recipes_stats['new_score'] = (
            poids_note * self.df_recipes_stats['mean_rating'] + 
            poids_nb_reviews * self.df_recipes_stats['rewarded_nb_ratings']
        )
        self.df_recipes_stats['new_score'] = (self.df_recipes_stats['new_score'] / np.max(self.df_recipes_stats['new_score'])) * 100
        return self.df_recipes_stats['new_score']

    def empirical_cdf(self, data):
        """
        Calcule la fonction de répartition empirique (CDF) pour un ensemble de données.

        Parameters:
        data (array-like): Les données pour lesquelles calculer la CDF.

        Returns:
        tuple: Les données triées et la CDF empirique correspondante.
        """
        sorted_data = np.sort(data)
        cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
        return sorted_data, cdf

    def objective(self, poids_note):
        """
        Calcule l'erreur quadratique moyenne entre la CDF empirique des scores et la CDF théorique normale.

        Parameters:
        poids_note (float): Le poids attribué aux notes moyennes.

        Returns:
        float: L'erreur quadratique moyenne entre la CDF empirique et la CDF théorique.
        """
        scores = self.compute_score(poids_note)
        sorted_scores, cdf_empirical = self.empirical_cdf(scores)
        mu, std = norm.fit(scores)
        cdf_theoretical = norm.cdf(sorted_scores, loc=mu, scale=std)
        mse = np.mean((cdf_empirical - cdf_theoretical) ** 2)
        return mse

    def optimize_weights(self):
        """
        Optimise les poids pour minimiser l'erreur quadratique moyenne entre la CDF empirique et la CDF théorique.

        Returns:
        tuple: Les poids optimisés pour les notes moyennes et le nombre de notes.
        """
        bounds = [(0, 1)]
        result = minimize(self.objective, x0=[0.5], bounds=bounds)
        return result.x[0], 1 - result.x[0]