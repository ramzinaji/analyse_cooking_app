import pandas as pd
from collections import Counter
import inflect
from sklearn.preprocessing import normalize
import numpy as np
import spacy
import streamlit as st
import matplotlib.pyplot as plt


from scipy.stats import norm
from scipy.optimize import minimize


class Preprocessing:
    def __init__(self, df_raw_recipes):
        """
        Initialise la classe avec le DataFrame brut contenant les recettes.
        :param df_raw_recipes: DataFrame contenant les données des recettes.
        """
        self.df_raw_recipes = df_raw_recipes
        self.nlp = spacy.load("en_core_web_sm")

    def create_monthly_dico_ingredient(self, month: int):
        """
        Crée un dictionnaire mensuel d'ingrédients pour un mois donné.
        :param month: Mois (1 à 12)
        :return: DataFrame contenant les ingrédients agrégés par année.
        """
        df = {}
        for year in range(2000, 2018):
            A = []
            X = self.df_raw_recipes[
                (self.df_raw_recipes['submitted'].dt.year == year) &
                (self.df_raw_recipes['submitted'].dt.month == month)
            ].ingredients
            for index in range(X.shape[0]):
                A += X.iloc[index]
            df['X_' + str(year)] = Counter(A)
            df['X_' + str(year)]['nbre_recipes'] = X.shape[0]
            df['X_' + str(year)]['nbre_ingredients'] = len(A)

        Month_Ingredients = pd.DataFrame(df).T.fillna(0)
        return Month_Ingredients

    @staticmethod
    def count_ingredients(df_ingredient: pd.DataFrame):
        """
        Compte les ingrédients et calcule leur fréquence d'apparition.
        :param df_ingredient: DataFrame contenant les ingrédients.
        :return: DataFrame avec les apparitions et les fréquences triées.
        """
        df_ingredient_all = pd.DataFrame(df_ingredient.sum()).reset_index()
        df_ingredient_all.columns = ['ingredients', 'appearances']
        df_ingredient_all['freq'] = (
            df_ingredient_all['appearances'] /
            df_ingredient.sum().loc['nbre_recipes'] * 100
        )
        return df_ingredient_all.sort_values(by='freq', ascending=False)

    @staticmethod
    def plural_to_singular(word: str):
        """
        Convertit un mot au singulier.
        :param word: Mot à convertir.
        :return: Mot converti au singulier ou original si non applicable.
        """
        p = inflect.engine()
        singular_word = p.singular_noun(word)
        return singular_word if singular_word else word

    def lemmetize_and_sort(self, df_ingredient_all: pd.DataFrame):
        """
        Lemmatise, met les ingrédients au singulier et trie par fréquence.
        :param df_ingredient_all: DataFrame contenant les ingrédients et leurs fréquences.
        :return: DataFrame des ingrédients réduits, triés par fréquence.
        """
        df_ingredient_all['ingredient_tf'] = df_ingredient_all['ingredients'].apply(
            lambda x: self.plural_to_singular(str(self.nlp(x)).split()[-1])
        )
        Valuable_ingredient_shorted = {}
        for ingredient in df_ingredient_all.ingredient_tf.drop_duplicates().values:
            Valuable_ingredient_shorted[ingredient] = {
                'appearances': int(df_ingredient_all[
                    df_ingredient_all['ingredient_tf'] == ingredient].appearances.sum()),
                'freq': df_ingredient_all[
                    df_ingredient_all['ingredient_tf'] == ingredient].freq.sum()
            }
        Valuable_ingredient_shorted = pd.DataFrame(
            Valuable_ingredient_shorted).T.sort_values(by='freq', ascending=False)
        return Valuable_ingredient_shorted[
            (Valuable_ingredient_shorted['appearances'] < 1000) &
            (Valuable_ingredient_shorted['appearances'] > 1)
        ]

    def mapping(self):
        """
        Crée un dictionnaire de mapping entre les ingrédients originaux et leurs formes réduites.
        :return: Dictionnaire de mapping des ingrédients.
        """
        Mapping_ingredients = {}
        for i in range(1, 13):
            list_ingredient = self.create_monthly_dico_ingredient(
                i).columns.values
            for x in list_ingredient:
                token = self.plural_to_singular(str(self.nlp(x)).split()[-1])
                if x not in Mapping_ingredients.keys():
                    Mapping_ingredients[x] = token
        return Mapping_ingredients

    def tokenised_recipe(self, string, mapping_ingredinent):
        """
        Transforme une recette en une liste d'ingrédients tokenisés en utilisant le mapping des ingrédients.
        :param string: Texte de la recette.
        :return: Liste d'ingrédients tokenisés.
        """

        L = []
        for x in Counter(string).keys():
            try:
                L.append(mapping_ingredinent[x])
            except KeyError:
                continue
        return L


class SeasonalityChecker:
    def __init__(self, dico_all_month_ingredient):
        """
        Initialise la classe avec un dictionnaire contenant les données par mois.
        :param dico_all_month_ingredient: Dictionnaire des données mensuelles des ingrédients.
        """
        self.dico_all_month_ingredient = dico_all_month_ingredient
        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

    def plot_ingredient_frequency(self, input_1):
        """
        Affiche un graphique de la fréquence mensuelle de deux ingrédients.

        :param input_1: Nom du premier ingrédient.
        :param input_2: Nom du second ingrédient.
        :param dico_all_month_ingredient: Dictionnaire contenant les fréquences mensuelles des ingrédients.
        """
        # Récupération des fréquences pour les ingrédients sur 12 mois
        output_1 = []
        for month in range(1, 13):
            output_1.append(
                self.dico_all_month_ingredient[month].loc[input_1].freq)

        st.subheader(f"Fréquence d'apparition de {input_1}  sur 12 mois")

        # Création du graphique
        fig, ax = plt.subplots()
        ax.plot(range(1, 13), output_1, label=input_1, marker='o')
        ax.set_title(f'Fréquence mensuelle : {input_1} ')
        ax.set_xlabel('Month')
        ax.set_ylabel('Frequency (%)')
        # ax.set_ylim(0, 50)  # Échelle de 0 à 50 %
        ax.legend()
        ax.grid(True)

        # Affichage du graphique dans Streamlit
        st.pyplot(fig)

    def is_seasonal(self, ingredient):
        """
        Vérifie si un ingrédient est de saison pour un mois donné.
        :param ingredient: Nom de l'ingrédient.
        :param season: Numéro du mois (1 à 12).
        :return: Message indiquant la saisonnalité.
        """
        best_season = 0
        max_frequency = 0  # Comparateur des fréquences entre saisons

        try:
            for month in range(1, 13):
                freq = self.dico_all_month_ingredient[month].loc[ingredient].freq
                if freq > max_frequency:
                    max_frequency = freq
                    best_season = month

            if max_frequency == 0:
                return f"Your ingredient '{ingredient}' is not in our database."
            else:
                return f"You should  cook {ingredient} in {self.months[best_season - 1]}."
        except KeyError:
            return f"Your ingredient '{ingredient}' is not in our database."
        except Exception as e:
            return f"An error occurred: {e}"

    def ingredient_std(self, ingredient):
        """
        Calcule la variance et la distribution normalisée d'un ingrédient sur 12 mois.
        :param ingredient: Nom de l'ingrédient.
        :return: Tuple contenant les valeurs normalisées et l'écart type normalisé.
        """
        ingredient_values = []

        try:
            for month in range(1, 13):
                ingredient_values.append(
                    self.dico_all_month_ingredient[month].loc[ingredient].freq)

            ingredient_values = np.array(ingredient_values)

            # Normalisation des valeurs
            ingredient_values_norm = normalize(
                ingredient_values.reshape(
                    12, 1), norm='max', axis=0)
            sigma_norm = np.var(ingredient_values_norm)

            return ingredient_values_norm, np.sqrt(sigma_norm)
        except KeyError:
            return f"Your ingredient '{ingredient}' does not exist in the database."
        except Exception as e:
            return f"An error occurred: {e}"


class IngredientMatcher:
    def __init__(self, df_recipes_tokenised, dico_all_month_ingredient):
        """
        Initialise la classe avec un DataFrame contenant des recettes tokenisées.
        :param df_recipes_tokenised: DataFrame contenant les recettes avec des colonnes 'submitted' et 'ingredients'.
        """
        self.df_recipes_tokenised = df_recipes_tokenised
        self.dico_all_month_ingredient = dico_all_month_ingredient

    def ingredient_match(self, ing, month):
        """
        Trouve les ingrédients les plus souvent associés à un ingrédient donné pour un mois donné.
        :param ing: Ingrédient témoin.
        :param month: Mois cible (1 à 12).
        :return: Dictionnaire des ingrédients associés avec leur fréquence.
        """
        match = []

        for recipe in self.df_recipes_tokenised[
            self.df_recipes_tokenised['submitted'].dt.month == month
        ].ingredients:
            if ing in recipe:
                match.extend(recipe)

        return Counter(match)

    def check_elements_in_list(self, elements, lst):
        """
        Vérifie si tous les éléments d'une liste sont présents dans une autre liste.
        :param elements: Liste des éléments à vérifier.
        :param lst: Liste dans laquelle chercher.
        :return: True si tous les éléments sont présents, sinon False.
        """
        lst_set = set(lst)
        return all(el in lst_set for el in elements)

    def recipes_filter_by_ingredients(self, list_ingredient, month):
        """
        Filtre les recettes qui associent tous les ingrédients donnés pour un mois donné.
        :param list_ingredient: Liste des ingrédients à chercher.
        :param month: Mois cible (1 à 12).
        :return: Liste des indices des recettes correspondantes.
        """
        match_recipes = []

        for index, recipe in enumerate(
            self.df_recipes_tokenised[
                self.df_recipes_tokenised['submitted'].dt.month == month
            ].ingredients
        ):
            if self.check_elements_in_list(list_ingredient, recipe):
                match_recipes.append(
                    int(
                        self.df_recipes_tokenised[
                            self.df_recipes_tokenised['submitted'].dt.month == month
                        ].ingredients.index[index]
                    )
                )

        return match_recipes

    def ingredient_best_seasonal(self, ingredient):
        best_season = 0
        c = 0
        for month in range(1, 13):
            self.dico_all_month_ingredient[month].loc[ingredient].freq
            if c > self.dico_all_month_ingredient[month].loc[ingredient].freq:
                continue
            else:
                c = self.dico_all_month_ingredient[month].loc[ingredient].freq
                best_season = month
        if c == 0:
            return ('Your ingredient is not in our database')
        else:
            return best_season

    def ingredient_std(self, ingredient):
        ingredient_values = []

        for i in range(1, 13):
            if ingredient in self.dico_all_month_ingredient[i].index:
                ingredient_values.append(
                    self.dico_all_month_ingredient[i].loc[ingredient].freq)
            else:
                continue

        if len(ingredient_values) > 0:
            N = len(ingredient_values)
            ingredient_values = np.array(ingredient_values)

            ingredient_values_norm = normalize(
                ingredient_values.reshape(
                    N, 1), norm='max', axis=0)
            sigma_norm = np.var(ingredient_values_norm)

            return ingredient_values_norm, [
                np.sqrt(sigma_norm.reshape(-1).item()), N]
        else:
            return 0, 0

    def seasonal_recommendations(self, ingredient, n):
        threshold = 0.1
        season = self.ingredient_best_seasonal(ingredient)
        list_ingredients_match = list(
            self.ingredient_match(
                ingredient, season).keys())
        list_valuable_match = []
        c = 0

        # Filtrer la liste pour récupérer les n ingrédient avec la plus grande
        # variance
        while c < n:
            match = list_ingredients_match[c]
            std_result = self.ingredient_std(match)
            if std_result[1][1] < 12:
                list_valuable_match.append(match)

            elif std_result[1][0] > threshold:
                list_valuable_match.append(match)

            c += 1

        return self.recipes_filter_by_ingredients(list_valuable_match, season)

    def seasonal_recommendations_1(self, ingredient, n):
        threshold = 0.1
        season = self.ingredient_best_seasonal(ingredient)
        dico_ingredient = self.ingredient_match(ingredient, season)
        sorted_dict = dict(
            sorted(
                dico_ingredient.items(),
                key=lambda item: item[1],
                reverse=True))
        list_ingredients_match = list(sorted_dict.keys())
        list_valuable_match = []
        list_valuable_match.append(ingredient)
        c = 0
        total_count = 0

        while c < n:

            total_count += 1
            match = list_ingredients_match[total_count]

            # Obtenir les valeurs renvoyées par ingredient_std(match)
            std_result = self.ingredient_std(match)

            # Vérification et accès correct des éléments
            if isinstance(std_result[1], (list, tuple)
                          ) and len(std_result[1]) > 1:
                value = std_result[1][1]
            else:
                value = std_result[1]  # Si c'est un entier directement

            # Comparaison avec 12
            if value < 12:
                list_valuable_match.append(match)
                c += 1
            elif std_result[1][0] > threshold:
                list_valuable_match.append(match)
                c += 1

            # c += 1

        return self.recipes_filter_by_ingredients(
            list_valuable_match, season), list_valuable_match

    def ingredient_score(self, ingredient):

        std_result = self.ingredient_std(ingredient)

        if isinstance(std_result[1], (list, tuple)) and len(std_result[1]) > 1:
            nbre_month = std_result[1][1]
        else:
            nbre_month = std_result[1]

        if nbre_month < 12:
            return nbre_month

        else:
            return std_result[1][0]


#Classes scoring

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
        self.df_recipes_stats['rewarded_nb_ratings'] = self.df_recipes_stats['nb_ratings'].apply(
            self.reward_nb_ratings, log_max=log_max)
        self.df_recipes_stats['new_score'] = (
            poids_note * self.df_recipes_stats['mean_rating'] +
            poids_nb_reviews * self.df_recipes_stats['rewarded_nb_ratings']
        )
        self.df_recipes_stats['new_score'] = (
            self.df_recipes_stats['new_score'] / np.max(self.df_recipes_stats['new_score'])) * 100
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
