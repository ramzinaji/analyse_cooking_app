""" This module contains the functions used in the app.py file. """

def is_seasonal(ingredient,season,dico_all_month_ingredient):
    """function to check if an ingredient is seasonal or not"""
    S=["January" ,"February" ,"March" ,"April" ,"May" ,"June" "July" ,"August" ,"September" ,"October","November" ,"December" ]
    best_season=0
    c=0                                                     #Comparateur des fréquences entre saison
    for month in range(1,13):
        if c > dico_all_month_ingredient[month].loc[ingredient].freq:
            continue
        else :
            c= dico_all_month_ingredient[month].loc[ingredient].freq
            best_season=month
    if c == 0:
        return 'Your ingredient is not in our database'
    elif season == best_season:
        return 'Good choice,the best season to cook ' + ingredient + ' is ' +S[int(best_season)-1]
    else :
        return 'You should cook ' + ingredient + ' in '+ S[int(best_season)-1]
