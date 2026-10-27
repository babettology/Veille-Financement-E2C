"""
Collecte des appels à projets publiés sur Carenews.

La liste est triée du plus récent au plus ancien. On lit les pages une
par une et on s'arrête dès que plusieurs pages de suite ne contiennent
plus aucun appel ouvert.
"""

import re
import time
from urllib import robotparser
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

import config

BASE = "https://www.carenews.com"
LISTE = BASE + "/appels_a_projets"
HEADERS = {"User-Agent": f"VeilleE2C/1.0 (contact: {config.CONTACT})"}
COLONNES = ["Titre", "Descriptif", "Organisation", "Date de publication",
            "Date de clôture", "URL", "Source"]


def _texte(bloc, selecteur):
    el = bloc.select_one(selecteur)
    return " ".join(el.get_text().split()) if el else ""


def _date(chaine):
    m = re.search(r"\d{2}\.\d{2}\.\d{4}", chaine)
    return pd.to_datetime(m.group(), format="%d.%m.%Y") if m else pd.NaT


def analyser_page(html):
    """Extrait les annonces d'une page de liste Carenews."""
    soup = BeautifulSoup(html, "html.parser")
    offres = []
    for bloc in soup.select("div.job-thumbnail"):
        lien = bloc.select_one("h3.job-thumbnail__title a")
        if not lien:
            continue
        titre_brut = " ".join(lien.get_text().split())
        # Le titre se termine par " - Nom de l'organisation" : on le retire
        titre = re.sub(r"\s+-\s*[^-]*$", "", titre_brut).strip()
        suffixe = titre_brut[len(titre):].strip(" -")
        offres.append({
            "Titre": titre,
            "Descriptif": _texte(bloc, ".job-thumbnail__text"),
            "Organisation": _texte(bloc, ".job-thumbnail__company a") or suffixe,
            "Date de publication": _date(_texte(bloc, ".job-thumbnail__date-start")),
            "Date de clôture": _date(_texte(bloc, ".job-thumbnail__date-end")),
            "URL": urljoin(BASE, lien["href"]),
            "Source": "Carenews",
        })
    return offres


def acces_autorise():
    """Vérifie ce que dit le robots.txt de Carenews."""
    rp = robotparser.RobotFileParser(BASE + "/robots.txt")
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(HEADERS["User-Agent"], LISTE + "/2/")


def collecter(nb_pages_max=config.NB_PAGES_MAX, afficher=print):
    """Lit les pages et renvoie un DataFrame des offres récentes."""
    if not acces_autorise():
        raise PermissionError("Le robots.txt de Carenews refuse l'accès automatisé.")

    aujourdhui = pd.Timestamp.today().normalize()
    toutes, pages_sans_ouvert = [], 0

    with requests.Session() as session:
        session.headers.update(HEADERS)
        for p in range(1, nb_pages_max + 1):
            try:
                r = session.get(f"{LISTE}/{p}/", timeout=20)
                r.raise_for_status()
            except requests.RequestException as e:
                afficher(f"  Page {p} : erreur ({e}), page ignorée")
                time.sleep(config.PAUSE_ENTRE_PAGES * 2)
                continue

            offres = analyser_page(r.text)
            if not offres:
                afficher(f"  Page {p} vide, fin de la liste")
                break

            ouvertes = sum(1 for o in offres
                           if pd.notna(o["Date de clôture"]) and o["Date de clôture"] >= aujourdhui)
            toutes.extend(offres)
            afficher(f"  Page {p} : {len(offres)} offres dont {ouvertes} ouvertes")

            pages_sans_ouvert = pages_sans_ouvert + 1 if ouvertes == 0 else 0
            if pages_sans_ouvert >= config.PAGES_VIDES_AVANT_ARRET:
                afficher(f"  {pages_sans_ouvert} pages de suite sans appel ouvert, arrêt")
                break

            time.sleep(config.PAUSE_ENTRE_PAGES)

    df = pd.DataFrame(toutes, columns=COLONNES)
    return df.drop_duplicates(subset="URL").reset_index(drop=True)
