import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import ast
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import streamlit as st
import sys

nlp = spacy.load("en_core_web_sm")

# Load the data
sys.path.append('C:/Users/nawfal/Documents/telecom/periode1/kit_big_data/project/analyse_cooking_app/etude_app_cuisine/app/data/kaggle')

# df_interactions_train=pd.read_csv('./data/kaggle/interactions_test.csv')
df_pp_recipes=pd.read_csv('./data/kaggle/PP_recipes.csv')
# df_pp_users=pd.read_csv('./data/kaggle/PP_users.csv')
# df_RAW_interactions=pd.read_csv('./data/kaggle/RAW_interactions.csv')
df_RAW_recipes=pd.read_csv('.data/kaggle/RAW_recipes.csv')

# Preprocessed the data

df_RAW_recipes.submitted=pd.to_datetime(df_RAW_recipes.submitted)
df_RAW_recipes_merged=df_RAW_recipes.copy()
df_RAW_recipes_merged=df_RAW_recipes_merged.merge(df_pp_recipes,how='inner',on='id')
df_RAW_recipes_merged.ingredients =  df_RAW_recipes_merged.ingredients.apply(lambda x : ast.literal_eval(x) )


# Utils

def create_monthly_dico_ingredient(month : int):
    df = {}
    for year in range(2000,2018):
        A = []
        X = df_RAW_recipes_merged[(df_RAW_recipes_merged['submitted'].dt.year==year) & (df_RAW_recipes_merged['submitted'].dt.month==month)].ingredients
        for index in range(X.shape[0]):
            A += X.iloc[index]
        df['X_' + str(year)] = Counter(A)                                                                    
        df['X_' + str(year)]['nbre_recipes'] = X.shape[0]
        df['X_' + str(year)]['nbre_ingredients'] = len(A)
        
    Month_Ingredients=pd.DataFrame(df).T
    Month_Ingredients=Month_Ingredients.fillna(0)
    return Month_Ingredients

def count_ingredients(df_ingredient : pd.DataFrame):
    df_ingredient_all=pd.DataFrame(df_ingredient.sum())

    df_ingredient_all=df_ingredient_all.reset_index()
    df_ingredient_all.columns=['ingredients','apperences']                                                                    
    df_ingredient_all['freq'] = df_ingredient_all['apperences'] / df_ingredient.sum().loc['nbre_recipes'] *100        #Fréquence (%) d'apparition d'un ingrédients en Janvier

    df_ingredient_all=df_ingredient_all.sort_values(by='freq',ascending=False)

    return df_ingredient_all


def lemmetize_and_sort(df_ingredient_all):
    
    df_ingredient_all['ingredient_tf']=df_ingredient_all['ingredients'].apply(lambda x : str(nlp(x)).split()[-1])
    Valuable_ingredient_shorted={}

    # On récupère réduit chaque ingrédient à son dernier et compte les occurences des nouveaux ingrédients

    for ingredient in df_ingredient_all.ingredient_tf.drop_duplicates().values: 
        Valuable_ingredient_shorted[ingredient]={'apperences': int(df_ingredient_all[df_ingredient_all['ingredient_tf']==ingredient].apperences.sum()),
                                                    'freq'      :  df_ingredient_all[df_ingredient_all['ingredient_tf']==ingredient].freq.sum()      }

    # On récupère que les valeurs avec plus d'un apparition et moins de 1000

    Valuable_ingredient_shorted=pd.DataFrame(Valuable_ingredient_shorted).T.sort_values(by='freq',ascending=False)
    Valuable_ingredient_shorted[(Valuable_ingredient_shorted['apperences']<1000) & (Valuable_ingredient_shorted['apperences']>1)]
    
    return Valuable_ingredient_shorted

# Treat the datas

dico_all_month_ingredient={}
for month in range(1,13):
    dico_all_month_ingredient[month]=lemmetize_and_sort(count_ingredients(create_monthly_dico_ingredient(month)))

print(dico_all_month_ingredient[1])
