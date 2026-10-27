"""
Lance la veille complète :
    python veille.py               (lecture automatique jusqu'aux appels clos)
    python veille.py --pages 5     (limiter à 5 pages)

Résultats dans le dossier resultats/ :
    compte_rendu_AAAA-MM-JJ.md   compte rendu des offres les plus pertinentes
    veille_AAAA-MM-JJ.xlsx       fichier Excel pour l'équipe
    offres_AAAA-MM-JJ.csv        données brutes
"""

import argparse
from datetime import date
from pathlib import Path

import config
from rapport import creer_compte_rendu, creer_excel, offres_pertinentes
from scoring import charger_modele, scorer
from scraping import collecter


def main():
    parser = argparse.ArgumentParser(description="Veille appels à projets E2C Paris")
    parser.add_argument("--pages", type=int, default=config.NB_PAGES_MAX,
                        help="nombre maximum de pages Carenews à lire")
    parser.add_argument("--sortie", default="resultats", help="dossier des résultats")
    args = parser.parse_args()

    dossier = Path(args.sortie)
    dossier.mkdir(exist_ok=True)
    jour = date.today().isoformat()

    print("1/4 Collecte des offres sur Carenews")
    offres = collecter(nb_pages_max=args.pages)
    print(f"    {len(offres)} offres récupérées")
    if offres.empty:
        print("Aucune offre récupérée, arrêt.")
        return

    print("2/4 Chargement du modèle BERT (long la première fois)")
    modele = charger_modele()

    print("3/4 Calcul des scores")
    resultats = scorer(offres, modele)

    print("4/4 Création du compte rendu et de l'Excel")
    chemin_md = dossier / f"compte_rendu_{jour}.md"
    chemin_xlsx = dossier / f"veille_{jour}.xlsx"
    chemin_csv = dossier / f"offres_{jour}.csv"
    creer_compte_rendu(resultats, chemin_md)
    creer_excel(resultats, chemin_xlsx)
    resultats.to_csv(chemin_csv, index=False, encoding="utf-8-sig")

    print(f"\nTerminé · {len(offres_pertinentes(resultats))} appels ouverts pertinents")
    print(f"  {chemin_md}\n  {chemin_xlsx}\n  {chemin_csv}")


if __name__ == "__main__":
    main()
