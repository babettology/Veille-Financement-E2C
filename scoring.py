"""
Calcul du score de pertinence E2C.

Deux scores sont combinés :
- le score mots-clés, qui repère les termes précis (insertion, 16 à 25 ans…)
- le score BERT, qui repère les offres proches par le sens des 3 axes de l'E2C
"""

import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import config


def sans_accents(texte):
    """« Égalité des chances » devient « egalite des chances »."""
    texte = str(texte).replace("\u2019", "'").replace("\u2018", "'")  # apostrophes typographiques
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c)).lower()


MOTIFS = {
    groupe: (poids, re.compile(r"\b(" + "|".join(re.escape(m) for m in mots) + r")\b"))
    for groupe, (poids, mots) in config.CRITERES.items()
}


def score_mots_cles(texte, organisation):
    """Renvoie le score mots-clés et la liste des groupes trouvés."""
    texte = sans_accents(texte)
    organisation = sans_accents(organisation)
    score, trouves = 0, []

    for groupe, (poids, motif) in MOTIFS.items():
        if motif.search(texte):
            score += poids
            trouves.append(groupe)

    if "jeunes" in trouves and any(m in texte for m in config.MOTS_GENERAUX):
        score += config.BONUS_COMBINAISON

    if any(p in organisation for p in config.PARTENAIRES):
        score += config.BONUS_PARTENAIRE
        trouves.append("partenaire E2C")

    return score, trouves


def _normaliser(serie):
    ecart = serie.max() - serie.min()
    return (serie - serie.min()) / ecart if ecart else serie * 0


def charger_modele():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.MODELE_BERT)


def score_bert(textes, modele):
    """Similarité de chaque offre avec chacun des 3 axes et avec le profil négatif."""
    axes = list(config.PROFIL_E2C)
    emb_offres = modele.encode(textes, batch_size=64, show_progress_bar=False)

    sim_par_axe = []
    for axe in axes:
        _, phrases = config.PROFIL_E2C[axe]
        sim = cosine_similarity(emb_offres, modele.encode(phrases))
        sim_par_axe.append(sim.max(axis=1))       # meilleure phrase de l'axe
    sim_par_axe = np.column_stack(sim_par_axe)

    sim_negatif = cosine_similarity(emb_offres, modele.encode(config.PROFIL_NEGATIF)).max(axis=1)

    meilleur = sim_par_axe.max(axis=1)
    penalite = np.where(sim_negatif > meilleur, config.PENALITE_NEGATIF, 0.0)
    score = meilleur * (1 - penalite)
    axe = [axes[i] for i in sim_par_axe.argmax(axis=1)]
    return score, axe


def scorer(df, modele):
    """Ajoute au DataFrame les scores, l'axe, le projet et le statut."""
    df = df.copy()
    df["Organisation"] = df["Organisation"].fillna("").astype(str).str.strip()
    textes = (df["Titre"].fillna("") + ". " + df["Descriptif"].fillna("")).tolist()

    # Mots-clés
    res = [score_mots_cles(t, o) for t, o in zip(textes, df["Organisation"])]
    df["Score mots-clés"] = [s for s, _ in res]
    df["Mots-clés trouvés"] = [", ".join(g) for _, g in res]

    # BERT
    df["Score BERT"], df["Axe"] = score_bert(textes, modele)
    df["Projet à présenter"] = df["Axe"].map({a: p for a, (p, _) in config.PROFIL_E2C.items()})

    # Score final entre 0 et 1
    df["Score"] = (
        config.POIDS_MOTS_CLES * _normaliser(df["Score mots-clés"])
        + config.POIDS_BERT * _normaliser(df["Score BERT"])
    ).round(2)
    df["Score BERT"] = df["Score BERT"].round(2)

    # Statut
    aujourdhui = pd.Timestamp.today().normalize()
    df["Jours restants"] = (df["Date de clôture"] - aujourdhui).dt.days
    df["Statut"] = np.where(df["Jours restants"] >= 0, "Ouvert", "Clos")

    return df.sort_values("Score", ascending=False).reset_index(drop=True)
