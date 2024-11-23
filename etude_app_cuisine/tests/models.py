import pandas as pd
from collections import Counter
import inflect
from sklearn.preprocessing import normalize
import numpy as np
import spacy



class Preprocessing:
    def __init__(self, df_raw_recipes):
        """
        Initialise la classe avec le DataFrame brut contenant les recettes.
        :param df_raw_recipes: DataFrame contenant les données des recettes.
        """
        self.df_raw_recipes = df_raw_recipes
        self.mapping_ingredinent = {}
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
            df_ingredient_all['appearances'] / df_ingredient.sum().loc['nbre_recipes'] * 100
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
            lambda x: self.plural_to_singular(str(nlp(x)).split()[-1])
        )
        Valuable_ingredient_shorted = {}
        for ingredient in df_ingredient_all.ingredient_tf.drop_duplicates().values:
            Valuable_ingredient_shorted[ingredient] = {
                'appearances': int(df_ingredient_all[
                    df_ingredient_all['ingredient_tf'] == ingredient].appearances.sum()),
                'freq': df_ingredient_all[
                    df_ingredient_all['ingredient_tf'] == ingredient].freq.sum()
            }
        Valuable_ingredient_shorted = pd.DataFrame(Valuable_ingredient_shorted).T.sort_values(by='freq', ascending=False)
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
            list_ingredient = self.create_monthly_dico_ingredient(i).columns.values
            for x in list_ingredient:
                token = self.plural_to_singular(str(self.nlp(x)).split()[-1])
                if x not in Mapping_ingredients.keys():
                    Mapping_ingredients[x] = token
        return Mapping_ingredients

    def tokenised_recipe(self, string):
        """
        Transforme une recette en une liste d'ingrédients tokenisés en utilisant le mapping des ingrédients.
        :param string: Texte de la recette.
        :return: Liste d'ingrédients tokenisés.
        """
        L = []
        for x in Counter(string).keys():
            try:
                L.append(self.mapping_ingredinent[x])
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

    def is_seasonal(self, ingredient, season):
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
            elif season == best_season:
                return f"Good choice, the best season to cook {ingredient} is {self.months[best_season - 1]}."
            else:
                return f"You should not cook {ingredient} in {self.months[season - 1]}."
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
                ingredient_values.append(self.dico_all_month_ingredient[month].loc[ingredient].freq)

            ingredient_values = np.array(ingredient_values)
            sigma_ingredient = np.var(ingredient_values)

            # Normalisation des valeurs
            ingredient_values_norm = normalize(ingredient_values.reshape(12, 1), norm='max', axis=0)
            sigma_norm = np.var(ingredient_values_norm)

            return ingredient_values_norm, np.sqrt(sigma_norm)
        except KeyError:
            return f"Your ingredient '{ingredient}' does not exist in the database."
        except Exception as e:
            return f"An error occurred: {e}"
        
        

class IngredientMatcher:
    def __init__(self, df_recipes_tokenised):
        """
        Initialise la classe avec un DataFrame contenant des recettes tokenisées.
        :param df_recipes_tokenised: DataFrame contenant les recettes avec des colonnes 'submitted' et 'ingredients'.
        """
        self.df_recipes_tokenised = df_recipes_tokenised

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
