import os
from PIL import Image
from PIL.ExifTags import TAGS

# Dossier contenant les photos
DOSSIER = r"C:\MesPhotos"

def lire_date_photo(chemin):
    try:
        image = Image.open(chemin)
        exif = image.getexif()

        for tag_id, valeur in exif.items():
            nom_tag = TAGS.get(tag_id, tag_id)

            if nom_tag == "DateTimeOriginal":
                return valeur

        return "Date inconnue"

    except Exception:
        return "Erreur de lecture"


def analyser_photos():
    for fichier in os.listdir(DOSSIER):

        if fichier.lower().endswith(
            (".jpg", ".jpeg", ".tif", ".tiff")
        ):
            chemin = os.path.join(DOSSIER, fichier)

            date = lire_date_photo(chemin)

            print(f"{fichier} : {date}")


analyser_photos()
