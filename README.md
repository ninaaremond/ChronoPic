# ChronoPic

Application de bureau Python (Tkinter) pour analyser les dates EXIF et organiser une bibliothèque de photographies.

## Fonctionnalités
- Import d'un dossier ou de photos individuelles avec analyse EXIF automatique.
- Miniatures et aperçu sans recadrage, avec correction de l'orientation EXIF.
- Recherche par nom et filtres : présence de date, année et mois.
- Tri chronologique croissant ou décroissant et regroupement visuel par mois/année.
- Détails : date, source EXIF, appareil photo, dimensions, format et chemin.
- Export Excel des photos sélectionnées, avec un onglet dédié aux photos sans date.
- Génération d'un rapport texte de la session.
- Le menu « Actions » permet d'exporter le rapport ou de vider la galerie.
- Les fichiers photo originaux ne sont jamais modifiés.

## Installation
Python 3.10 ou plus récent recommandé.

```bash
python -m pip install -r requirements.txt
python main.py
```

## Dépendances
- Pillow
- openpyxl
