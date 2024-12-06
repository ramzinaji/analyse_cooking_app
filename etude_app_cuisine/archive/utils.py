import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize


def is_seasonal(ingredient, season, dico_all_month_ingredient):
    S = ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"]
    best_season = 0
    c = 0  # Comparateur des fréquences entre saison
    for month in range(1, 13):
        dico_all_month_ingredient[month].loc[ingredient].freq
        if c > dico_all_month_ingredient[month].loc[ingredient].freq:
            continue
        else:
            c = dico_all_month_ingredient[month].loc[ingredient].freq
            best_season = month
    if c == 0:
        return ('Your ingredient is not in our database')
    elif season == best_season:
        return ('Good choice, the best season to cook ' + ingredient + ' is ' + S[int(best_season)-1])
    else:
        return ('You should not cook ' + ingredient + ' in ' + S[int(season)-1])


def ingredient_std(ingredient, dico_all_month_ingredient):
    ingredient_values = []
    try:
        for i in range(1, 13):
            ingredient_values.append(
                dico_all_month_ingredient[i].loc[ingredient].freq)

        ingredient_values = np.array(ingredient_values)
        sigma_ingredient = np.var(ingredient_values)

        ingredient_values_norm = normalize(
            ingredient_values.reshape(12, 1), norm='max', axis=0)
        sigma_norm = np.var(ingredient_values_norm)

        return ingredient_values_norm, np.sqrt(sigma_norm.reshape(-1))

    except KeyError:
        print(ingredient + ' does not exist')

    except Exception as e:
        print(f"An error occurred: {e}")


def helloworld():
    print('Hello World')
