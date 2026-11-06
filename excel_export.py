
from openpyxl import Workbook

from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment
)


def export_to_excel(photos, path):

    analyzed = [
        photo for photo in photos
        if photo["statut"] != "En attente"
    ]

    if not analyzed:
        raise ValueError("Aucune photo analysée.")

    workbook = Workbook()
    sheet = workbook.active

    sheet.title = "ChronoPic"

    headers = [
        "Nom de la photo",
        "Date du cliché",
        "Métadonnée",
        "Statut",
        "Chemin du fichier"
    ]

    sheet.append(headers)

    # Mise en forme des en-têtes
    for cell in sheet[1]:

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            start_color="2878C8",
            end_color="2878C8",
            fill_type="solid"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # Ajout des photos
    for photo in analyzed:

        sheet.append([
            photo["nom"],
            photo["date_affichee"],
            photo["source"],
            photo["statut"],
            photo["chemin"]
        ])

    # Mise en forme du tableau
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    widths = {
        "A": 30,
        "B": 22,
        "C": 25,
        "D": 22,
        "E": 75
    }

    for column, width in widths.items():

        sheet.column_dimensions[column].width = width

    workbook.save(path)
