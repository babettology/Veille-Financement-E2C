"""
Réglages de la veille E2C Paris.

C'est le SEUL fichier à modifier pour ajuster la veille :
mots-clés, partenaires, profil de l'E2C, seuils.
Pas besoin de toucher aux autres fichiers.
"""

# ---------------------------------------------------------------
# Collecte
# ---------------------------------------------------------------
NB_PAGES_MAX = 47          # nombre maximum de pages Carenews à lire
PAGES_VIDES_AVANT_ARRET = 2  # arrêt après N pages de suite sans appel ouvert
PAUSE_ENTRE_PAGES = 3      # secondes de pause entre deux pages (politesse)
CONTACT = "ton.email@exemple.fr"  # à remplacer par une adresse de l'E2C

# ---------------------------------------------------------------
# Score final
# ---------------------------------------------------------------
POIDS_MOTS_CLES = 0.5      # part du score mots-clés dans le score final
POIDS_BERT = 0.5           # part du score BERT (la somme doit faire 1)
SEUIL_PERTINENCE = 0.6     # score minimum pour figurer dans le compte rendu
URGENCE_JOURS = 15         # clôture sous N jours = urgent
NB_OFFRES_RAPPORT = 20     # nombre maximum d'offres dans le compte rendu

# ---------------------------------------------------------------
# Mots-clés pondérés (écrits SANS accents et en minuscules)
# groupe : (poids, [mots-clés])
# ---------------------------------------------------------------
CRITERES = {
    "insertion / emploi": (5, [
        "insertion", "insertion professionnelle", "emploi", "employabilite",
        "formation", "formation professionnelle", "chomage", "decrochage",
        "decrocheur", "neet", "sans diplome", "qualification",
        "eloignes de l'emploi", "metiers en tension",
    ]),
    "jeunes": (4, [
        "jeune", "jeunes", "jeunesse", "16 a 25 ans", "16-25", "18-25",
        "education", "aide sociale a l'enfance", "primo-arrivant",
        "primo-arrivants", "quartiers prioritaires", "qpv",
        "sous main de justice",
    ]),
    "égalité / inclusion": (3, [
        "egalite", "egalite des chances", "inclusion", "handicap",
        "discrimination", "discriminations", "accessibilite",
    ]),
    "femmes": (3, [
        "femme", "femmes", "jeunes filles", "egalite femmes-hommes",
    ]),
    "citoyenneté": (2, [
        "citoyennete", "citoyen", "citoyenne", "engagement", "benevolat",
        "democratie", "solidarite", "memoire", "defense",
    ]),
    "parcours citoyen": (2, [
        "sport", "culture", "environnement", "transition ecologique",
        "metiers verts", "education aux medias", "esprit critique",
    ]),
    "pédagogie": (2, [
        "competence", "competences", "stage", "alternance", "apprentissage",
        "accompagnement", "savoir-etre", "orientation", "mentorat",
    ]),
    "territoire": (3, [
        "paris", "ile-de-france", "francilien", "francilienne", "national",
        "nationale", "toute la france", "france entiere",
    ]),
    "hors cible": (-4, [
        "recherche medicale", "chercheurs", "patients", "doctorant",
        "seniors", "petite enfance", "lille", "lyon", "marseille",
        "bordeaux", "toulouse", "nantes", "hauts-de-france", "auvergne",
        "occitanie", "bretagne",
    ]),
}

# Bonus si un mot général apparaît AVEC un mot du groupe "jeunes"
MOTS_GENERAUX = ["emploi", "formation", "inclusion", "egalite"]
BONUS_COMBINAISON = 2

# Organisations déjà liées à l'E2C (membres du CA, partenaires du Parcours)
PARTENAIRES = [
    "ratp", "sncf", "edf", "la poste", "monoprix", "enedis", "paris habitat",
    "clariane", "compass", "croix-rouge", "makesense", "memorial de la shoah",
    "armee de terre", "ville de paris",
]
BONUS_PARTENAIRE = 3

# ---------------------------------------------------------------
# Profil de l'E2C pour BERT : 3 axes, phrases courtes
# axe : (projet à présenter, [phrases])
# ---------------------------------------------------------------
PROFIL_E2C = {
    "Insertion des jeunes": ("E2C Paris", [
        "Accompagner vers l'emploi ou la formation qualifiante des jeunes de 16 à 25 ans peu ou pas diplômés.",
        "Favoriser l'insertion professionnelle de jeunes éloignés de l'emploi, sans qualification ni réseau.",
        "Lutter contre le décrochage scolaire et offrir une deuxième chance aux jeunes sortis de l'école.",
        "Accompagner les jeunes des quartiers prioritaires, primo-arrivants ou sous main de justice.",
        "Parcours d'insertion alternant ateliers et stages en entreprise pour construire un projet professionnel.",
    ]),
    "Engagement citoyen": ("Parcours Engagement Citoyen", [
        "Développer l'engagement citoyen et le pouvoir d'agir des jeunes.",
        "Sensibiliser les jeunes à la démocratie, à la mémoire et aux valeurs de la défense.",
        "Mener avec des jeunes des actions solidaires et de préservation de l'environnement.",
        "Favoriser l'accès des jeunes à la culture et valoriser leur expression.",
        "Utiliser le sport comme outil de cohésion et de dépassement de soi pour les jeunes.",
    ]),
    "Égalité et inclusion": ("E2C Paris ou Parcours", [
        "Promouvoir l'égalité des chances et lutter contre les discriminations chez les jeunes.",
        "Favoriser l'inclusion professionnelle des jeunes en situation de handicap.",
        "Favoriser l'insertion professionnelle et l'autonomie des jeunes femmes.",
        "Développer l'esprit critique des jeunes et l'éducation aux médias.",
    ]),
}

# Ce que l'E2C n'est PAS : une offre plus proche de ces phrases perd des points
PROFIL_NEGATIF = [
    "Financement de la recherche médicale ou scientifique.",
    "Bourses individuelles pour des étudiants ou des doctorants.",
    "Soutien à des start-up ou entreprises à but lucratif.",
    "Projets en faveur des personnes âgées ou de la petite enfance.",
]
PENALITE_NEGATIF = 0.5     # part du score BERT retirée si l'offre ressemble plus au négatif

MODELE_BERT = "paraphrase-multilingual-MiniLM-L12-v2"
