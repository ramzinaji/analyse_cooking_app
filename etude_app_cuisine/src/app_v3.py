import streamlit as st
import logging
import os


# -----------------------------------
# Logging Setup
# -----------------------------------

# Define the path to the log file
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "streamlit_app.log")

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Log an initialization message
logging.info("Streamlit application initialized.")

st.set_page_config(
    page_title="Page de Garde - Projet d'Analyse de Recettes",
    page_icon="🍽",
    layout="wide"
)

st.page_link("app_v3.py", label="Home", icon="🏠")
st.page_link("pages/page1.py", label="Page 1", icon="1️⃣")
st.page_link("pages/page2.py", label="Page 2", icon="2️⃣")
st.page_link("http://www.google.com", label="Google", icon="🌎")

# Log page load
logging.info("Main page loaded.")

# Section Auteurs
st.markdown("""
### Auteurs
- ADIL Nawfal
- ESKINAZI Etienne
- MALAININE Mohamed Limame
- NAJI Ramzi
""")

# Titre principal
st.title("Projet Kit Big Data - Méthode de scoring des recettes et Analyse de la saisonnalité des ingrédients")

# Sous-titre / Introduction
st.markdown("""
### Pourquoi cette application ?

Nous sommes convaincus que cuisiner, c’est plus qu’une simple activité : c’est une manière de se reconnecter
au goût, à la nature et aux autres. Dans un monde où tout semble aller trop vite, où l’on consomme sans réfléchir,
cette application s’inscrit dans un mouvement qui valorise **le "manger mieux"**.

Notre outil vous permet de découvrir des recettes qui ne sont pas juste populaires, mais qui s’appuient sur
des ingrédients frais et de saison.

Cette application est votre compagnon idéal pour cuisiner de manière responsable et savoureuse !

### Présentation Générale

Ce projet vise à développer un outil de recommandation culinaire en s’appuyant sur trois axes principaux :

1. **Une nouvelle méthode de scoring basée sur la popularité des recettes** :
   Nous avons d’abord étudié la distribution des notes attribuées par les utilisateurs et constaté qu’elles
   sont trop homogènes. Nous en avons conclu que cette seule variable n'est pas suffisante pour classer les
   recettes du fait d'une trop grande homogénéité des notes. Nous avons donc dans un second temps cherché à
   déterminer une meilleure approche pour classer les recettes.
   Ainsi, nous avons intégré le nombre de commentaires données par les utilisateurs à chaque recette,
   qui s'est avérée être une variable plus discriminante. Nous avons alors décidé de proposer un nouveau score
   prenant en compte à la fois la qualité de la recette (note moyenne) et sa popularité (nombre de commentaires).
   Cette nouvelle métrique, plus représentative et plus proche d’une distribution idéale (loi normale),
   garantit une meilleure hiérarchisation des recettes.

2. **L'analyse de la saisonnalité des ingrédients** :
   Nos données révèlent comment la popularité des ingrédients varie au fil de l’année. Notre application
   permet d’identifier quand un ingrédient est "de saison", et propose un calendrier culinaire qui met en avant
   l’utilisation d’ingrédients au bon moment de l’année.

3. **La recommandation de recettes saisonnières** :
   En tenant compte de la saisonnalité et de la popularité des ingrédients, l’application propose des
   combinaisons cohérentes et des recettes adaptées à la période de l’année, incitant l’utilisateur à privilégier
   des ingrédients de saison.
""")

# Explication de la structure de l'application
st.markdown("""
### Structure de l’Application Streamlit

- **Page d’Analyse des Notes et Reviews (page1.py)** :
  Cette page explore la distribution des notes, compare différentes lois de probabilité et introduit la nouvelle
  méthode de scoring. Elle présente aussi la logique de pondération entre la qualité perçue (note) et la popularité
  (nombre de commentaires), ainsi que son optimisation. Le tout est illustré par des visualisations claires et
  interactives.

- **Page d’Analyse de la Saison & Recommandations (page2.py)** :
  Cette page présente la fréquence mensuelle des ingrédients et leur variation saisonnière. L’utilisateur peut
  y entrer un ingrédient pour savoir quand l’utiliser au mieux. Il peut également découvrir des ingrédients
  complémentaires et accéder à des recettes populaires (selon notre propre score) basées sur ces ingrédients de
  saison.
""")

# Log successful completion of page
logging.info("Main page content rendered successfully.")
