
import os

from config import SUPPORTED_EXTENSIONS


class PhotoManager:

    def __init__(self):
        self.photos = []

    # ==========================================
    # CREATION D'UNE ENTREE PHOTO
    # ==========================================

    def create_photo(self, path):

        return {
            "chemin": path,
            "nom": os.path.basename(path),
            "date": None,
            "date_affichee": "Non analysée",
            "source": "",
            "statut": "En attente",
            "selection": True
        }

    # ==========================================
    # SELECTION D'UN DOSSIER
    # ==========================================

    def load_folder(self, folder):

        if not os.path.isdir(folder):
            return 0

        files = []

        for filename in os.listdir(folder):

            path = os.path.join(folder, filename)

            if (
                os.path.isfile(path)
                and filename.lower().endswith(SUPPORTED_EXTENSIONS)
            ):
                files.append(path)

        return self.add_photos(files)

    # ==========================================
    # AJOUT DE PHOTOS
    # ==========================================

    def add_photos(self, files):

        existing = {
            photo["chemin"]
            for photo in self.photos
        }

        added = 0

        for path in files:

            path = os.path.abspath(path)

            if (
                os.path.isfile(path)
                and path.lower().endswith(SUPPORTED_EXTENSIONS)
                and path not in existing
            ):

                self.photos.append(
                    self.create_photo(path)
                )

                existing.add(path)
                added += 1

        return added

    # ==========================================
    # SUPPRESSION
    # ==========================================

    def clear(self):
        self.photos.clear()

    # ==========================================
    # TRI CHRONOLOGIQUE
    # ==========================================

    def sort_chronologically(self):

        from datetime import datetime

        self.photos.sort(
            key=lambda photo: (
                photo["date"] is None,
                photo["date"] or datetime.max
            )
        )

    # ==========================================
    # SELECTION
    # ==========================================

    def select_all(self, value=True):

        for photo in self.photos:
            photo["selection"] = value

    def get_selected(self):

        return [
            photo for photo in self.photos
            if photo["selection"]
        ]

    def get_count(self):
        return len(self.photos)

    def get_analyzed_count(self):

        return sum(
            1 for photo in self.photos
            if photo["statut"] != "En attente"
        )

    def get_dated_count(self):

        return sum(
            1 for photo in self.photos
            if photo["date"] is not None
        )

    def get_undated_count(self):

        return sum(
            1 for photo in self.photos
            if photo["statut"] not in (
                "En attente",
                "Date trouvée"
            )
        )

    def get_filtered(self, search="", date_filter="Toutes", year="Toutes", month="Tous",
                     selected_only=False, descending=False):
        """Construit une vue filtrée sans modifier la collection originale."""
        items = self.photos
        query = search.casefold().strip()
        if query:
            items = [p for p in items if query in p["nom"].casefold()]
        if date_filter == "Avec date":
            items = [p for p in items if p["date"] is not None]
        elif date_filter == "Sans date":
            items = [p for p in items if p["statut"] != "En attente" and p["date"] is None]
        if selected_only:
            items = [p for p in items if p["selection"]]
        if year != "Toutes":
            items = [p for p in items if p["date"] and str(p["date"].year) == str(year)]
        if month != "Tous":
            items = [p for p in items if p["date"] and p["date"].month == int(month)]
        dated = [p for p in items if p["date"] is not None]
        undated = [p for p in items if p["date"] is None]
        dated.sort(key=lambda p: p["date"], reverse=descending)
        return dated + undated
