
import io

from PIL import Image, ImageOps

from config import (
    THUMBNAIL_WIDTH,
    THUMBNAIL_HEIGHT,
    THUMBNAIL_QUALITY,
    PREVIEW_WIDTH,
    PREVIEW_HEIGHT
)


def create_thumbnail(path):
    """
    Génère une miniature sans recadrage.

    Retourne des données JPEG en mémoire.
    """

    try:

        with Image.open(path) as image:

            # Correction de l'orientation EXIF
            image = ImageOps.exif_transpose(image)

            # Redimensionnement sans déformation
            image = ImageOps.contain(
                image,
                (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
                method=Image.Resampling.LANCZOS
            )

            image = image.convert("RGB")

            # Fond gris fixe
            background = Image.new(
                "RGB",
                (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
                "#EEEEEE"
            )

            # Centrage de la photographie
            x = (THUMBNAIL_WIDTH - image.width) // 2
            y = (THUMBNAIL_HEIGHT - image.height) // 2

            background.paste(image, (x, y))

            buffer = io.BytesIO()

            background.save(
                buffer,
                format="JPEG",
                quality=THUMBNAIL_QUALITY
            )

            return buffer.getvalue()

    except Exception:
        return None


def create_preview(path):
    """
    Génère un aperçu grand format sans recadrage.
    """

    try:

        with Image.open(path) as image:

            image = ImageOps.exif_transpose(image)

            image = ImageOps.contain(
                image,
                (PREVIEW_WIDTH, PREVIEW_HEIGHT),
                method=Image.Resampling.LANCZOS
            )

            image = image.convert("RGB")

            background = Image.new(
                "RGB",
                (PREVIEW_WIDTH, PREVIEW_HEIGHT),
                "#222222"
            )

            x = (PREVIEW_WIDTH - image.width) // 2
            y = (PREVIEW_HEIGHT - image.height) // 2

            background.paste(image, (x, y))

            return background

    except Exception:
        return None
