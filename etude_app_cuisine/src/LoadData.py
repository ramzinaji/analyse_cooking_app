import gdown
import os

# Récupérer le répertoire actuel
current_directory = os.getcwd()

# Lister tous les fichiers et répertoires dans le répertoire actuel
files_and_dirs = os.listdir(current_directory)

# Afficher les résultats
print("Fichiers et répertoires dans le répertoire actuel :")
for item in files_and_dirs:
    print(item)

url = 'https://drive.google.com/uc?id='
url_df_recipes_tokenised  = url +'10aFfjOWpo4p42wNvRERYqygEEy9gTiK0'
url_dico_all_month_ingredient1 = url + '1SLpu0QftR6sxm-B-ZO7w8JTcunTSqRO1'
url_dico_all_month_ingredient2 = url + '1jeBNRknK3_OPN-eJ9nAgCDBwEK_80aLr'
url_dico_all_month_ingredient3 = url + '1gnHyFY_48YyfTgchNqdYnxJY1YDMZ9ox'
url_dico_all_month_ingredient4 = url + '1FyTs3phgZCBsrzRya4sSOQ0HPI16Qkkx'
url_dico_all_month_ingredient5 = url + '1Kos2HlH9XbG0tTlVXlPpt4WrTVyx4DRl'
url_dico_all_month_ingredient6 = url + '1-Opzgg4xfwmF0aglnQdmv8Hsi3KdTPnq'
url_dico_all_month_ingredient7 = url + '1UwLxPsO8p5l1hCNM8arOvwOnULN6Pztj'
url_dico_all_month_ingredient8 = url + '1ndHDqjfJLweZFi8cdm0ffXkuaXfGbIQC'
url_dico_all_month_ingredient9 = url + '1Qq3xt74_CzR7jU8zWsX0aPckVXHCk83H'
url_dico_all_month_ingredient10 = url + '1X20cYFJYjJ61f9JCeUaMzMO8PnAetoV0'
url_dico_all_month_ingredient11 = url + '1CItK_q5r2uaRFRj1DsQlsb_DwYUSfN7q'
url_dico_all_month_ingredient12 = url + '1HD2iIHzReNybdcdPxKpLQqrM3AXPSAoN'
url_mapping = url + '1KWG2sRTxr74Opcth0dFF8fjNUU5qw3Te'
url_RAW_interactions = url + '13SSK3DpPw9Az7bcIFja_qIpJARGoHHAr'
url_RAW_recipes = url + '1GTx6HsCIoWKlGetIC_2KQWMEtJ-3Hts3'

List_url = [
    url_df_recipes_tokenised,
    url_dico_all_month_ingredient1,
    url_dico_all_month_ingredient2,
    url_dico_all_month_ingredient3,
    url_dico_all_month_ingredient4,
    url_dico_all_month_ingredient5,
    url_dico_all_month_ingredient6,
    url_dico_all_month_ingredient7,
    url_dico_all_month_ingredient8,
    url_dico_all_month_ingredient9,
    url_dico_all_month_ingredient10,
    url_dico_all_month_ingredient11,
    url_dico_all_month_ingredient12,
    url_mapping,
    url_RAW_interactions,
    url_RAW_recipes
]

List_output =[
    'df_recipes_tokenised.json',
    'dico_all_month_ingredient1.csv',
    'dico_all_month_ingredient2.csv',
    'dico_all_month_ingredient3.csv',
    'dico_all_month_ingredient4.csv',
    'dico_all_month_ingredient5.csv',
    'dico_all_month_ingredient6.csv',
    'dico_all_month_ingredient7.csv',
    'dico_all_month_ingredient8.csv',
    'dico_all_month_ingredient9.csv',
    'dico_all_month_ingredient10.csv',
    'dico_all_month_ingredient11.csv',
    'dico_all_month_ingredient12.csv',
    'mapping.json',
    'RAW_interactions.csv',
    'RAW_recipes.csv'
]

path = 'etude_app_cuisine/src/data_loaded/'
for i in range(len(List_url)):
    gdown.download(List_url[i], path + List_output[i], quiet=False)
    print(f'Fichier téléchargé : {List_output[i]}')