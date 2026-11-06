
from PIL import Image
from datetime import datetime


def read_photo_date(path):
    """
    Lit les métadonnées EXIF d'une photo.

    Priorité :
    1. DateTimeOriginal
    2. DateTimeDigitized
    3. DateTime

    Retourne :
    (date, source)
    """

    try:
        with Image.open(path) as image:

            exif = image.getexif()

            try:
                exif_detail = exif.get_ifd(0x8769)
            except Exception:
                exif_detail = {}

            dates = [
                (exif_detail.get(36867), "DateTimeOriginal"),
                (exif_detail.get(36868), "DateTimeDigitized"),
                (exif.get(306), "DateTime")
            ]

            for value, source in dates:

                if not value:
                    continue

                if isinstance(value, bytes):
                    value = value.decode(
                        "utf-8",
                        errors="replace"
                    )

                try:
                    date = datetime.strptime(
                        str(value).strip(),
                        "%Y:%m:%d %H:%M:%S"
                    )

                    return date, source

                except ValueError:
                    continue

            return None, "Aucune date EXIF"

    except Exception:
        return None, "Erreur de lecture"


def format_photo_date(date):
    """
    Formate une date pour l'affichage.
    """

    if date is None:
        return "Inconnue"

    return date.strftime("%d/%m/%Y %H:%M:%S")
