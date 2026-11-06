from datetime import datetime
from PIL import Image, ExifTags

def read_photo_metadata(path):
    """Retourne les métadonnées utiles sans modifier le fichier original."""
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            try:
                detail = exif.get_ifd(0x8769)
            except Exception:
                detail = {}
            candidates = [
                (detail.get(36867), "DateTimeOriginal"),
                (detail.get(36868), "DateTimeDigitized"),
                (exif.get(306), "DateTime"),
            ]
            date = None
            source = "Aucune date EXIF"
            for value, label in candidates:
                if not value:
                    continue
                if isinstance(value, bytes):
                    value = value.decode("utf-8", errors="replace")
                try:
                    date = datetime.strptime(str(value).strip(), "%Y:%m:%d %H:%M:%S")
                    source = label
                    break
                except ValueError:
                    continue
            make = exif.get(271, "")
            model = exif.get(272, "")
            camera = " ".join(str(x).strip() for x in (make, model) if x).strip() or "Non renseigné"
            width, height = image.size
            return {"date": date, "source": source, "appareil": camera,
                    "largeur": width, "hauteur": height, "format": image.format or "Inconnu"}
    except Exception:
        return {"date": None, "source": "Erreur de lecture", "appareil": "Non renseigné",
                "largeur": None, "hauteur": None, "format": "Illisible"}

def read_photo_date(path):
    metadata = read_photo_metadata(path)
    return metadata["date"], metadata["source"]

def format_photo_date(date):
    return date.strftime("%d/%m/%Y %H:%M:%S") if date else "Inconnue"
