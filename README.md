# Veille appels à projets · E2C Paris

Outil qui récupère les appels à projets publiés sur [Carenews](https://www.carenews.com/appels_a_projets), les classe selon leur proximité avec les missions de l'E2C Paris, et produit un compte rendu des offres les plus pertinentes.

## Ce que produit l'outil

| Fichier | Contenu |
|---|---|
| `resultats/compte_rendu_AAAA-MM-JJ.md` | Compte rendu lisible des appels ouverts les plus pertinents, avec les urgences en tête |
| `resultats/veille_AAAA-MM-JJ.xlsx` | Excel pour l'équipe (onglets À traiter, Toutes les offres, Financeurs, Avis) |
| `resultats/offres_AAAA-MM-JJ.csv` | Données brutes |

## Comment le score est calculé

Chaque offre reçoit un score de 0 à 1, moyenne de deux mesures.

| Mesure | Ce qu'elle repère |
|---|---|
| Score mots-clés | Les termes liés aux missions de l'E2C (insertion, jeunes de 16 à 25 ans, égalité des chances, partenaires…) |
| Score BERT | La proximité de sens avec les trois axes de l'E2C, même quand l'offre n'emploie pas les mots-clés |

Les trois axes et le projet associé.

| Axe | Projet à présenter |
|---|---|
| Insertion des jeunes | E2C Paris |
| Engagement citoyen | Parcours Engagement Citoyen |
| Égalité et inclusion | E2C Paris ou Parcours |

## Les fichiers

| Fichier | Rôle | À modifier ? |
|---|---|---|
| `config.py` | Mots-clés, partenaires, phrases du profil E2C, seuils | **Oui**, c'est le seul fichier à toucher |
| `scraping.py` | Récupération des offres sur Carenews | Non |
| `scoring.py` | Calcul des scores | Non |
| `rapport.py` | Compte rendu et Excel | Non |
| `veille.py` | Lance l'ensemble | Non |

## Lancer la veille

### Sur son ordinateur

```bash
pip install -r requirements.txt
python veille.py
```

Pour aller plus vite pendant un test, limiter le nombre de pages.

```bash
python veille.py --pages 5
```

La première exécution télécharge le modèle BERT (environ 470 Mo), les suivantes sont plus rapides.

### Sur Google Colab

```python
!git clone https://github.com/NOM-DU-COMPTE/veille-e2c.git
%cd veille-e2c
!pip install -q -r requirements.txt
!python veille.py --pages 10
```

Les résultats apparaissent dans le dossier `resultats` du panneau Fichiers.

### Depuis GitHub, sans rien installer

Onglet **Actions**, puis **Veille Carenews**, puis **Run workflow**. Le compte rendu est ajouté au dossier `resultats/` et l'Excel est téléchargeable en bas de la page du lancement. Certains sites bloquent les serveurs de GitHub, si la collecte échoue il faut lancer la veille depuis un ordinateur.

## Ajuster la veille

| Besoin | Où, dans `config.py` |
|---|---|
| Ajouter un mot-clé | `CRITERES`, dans le groupe voulu, écrit sans accents |
| Ajouter un partenaire | `PARTENAIRES` |
| Recevoir plus ou moins d'offres | `SEUIL_PERTINENCE` (0.6 par défaut) |
| Ajouter un projet à financer | `PROFIL_E2C`, nouvel axe avec 3 ou 4 phrases courtes |
| Écarter un type d'appel | `PROFIL_NEGATIF` ou groupe `hors cible` de `CRITERES` |

## Bon usage

Le robots.txt de Carenews ne souhaite pas d'accès automatisé. L'outil lit donc les pages lentement (pause de 3 secondes), s'arrête dès qu'il n'y a plus d'appels ouverts, et doit être lancé avec modération, par exemple une fois par semaine.
