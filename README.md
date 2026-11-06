# 📸 ChronoPic

**ChronoPic** est une application Python permettant d'analyser les métadonnées EXIF des photographies afin de retrouver leur date de prise de vue et de faciliter leur classement chronologique.

## Fonctionnalités

- Sélection d'un dossier complet de photographies.
- Sélection individuelle de plusieurs images.
- Galerie avec prévisualisation des photographies.
- Miniatures avec conservation des proportions originales.
- Aperçu grand format sans recadrage.
- Sélection individuelle par cases à cocher.
- Analyse des métadonnées EXIF en arrière-plan.
- Classement chronologique automatique.
- Pagination de la galerie.
- Identification des photos sans date.
- Export des résultats au format Excel.

## Technologies

- Python 3
- Tkinter
- Pillow
- OpenPyXL
- Threading

## Installation

Cloner le repository :

```bash
git clone URL_DU_REPOSITORY
cd ChronoPic
```

Installer les dépendances :

```bash
py -m pip install -r requirements.txt
```

Lancer l'application :

```bash
py main.py
```

## Architecture

```text
ChronoPic/
├── main.py
├── interface.py
├── photo_manager.py
├── exif_reader.py
├── thumbnail.py
├── excel_export.py
├── config.py
├── assets/
├── requirements.txt
├── README.md
└── .gitignore
```

## Philosophie

ChronoPic est conçu pour simplifier l'organisation des collections photographiques, notamment pour retrouver les dates de clichés anciens.

L'application analyse les fichiers sans modifier, déplacer ou supprimer les photographies originales.

## Évolutions envisagées

- Visionneuse plein écran.
- Navigation entre les photographies.
- Filtres par année et par mois.
- Cache permanent des miniatures.
- Gestion des photos numérisées.
- Création d'un exécutable Windows.

---

*Projet personnel développé en Python.*