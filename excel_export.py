from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def export_to_excel(photos, path, selected_only=False):
    analyzed = [p for p in photos if p.get("statut") != "En attente"]
    if selected_only:
        analyzed = [p for p in analyzed if p.get("selection")]
    if not analyzed:
        raise ValueError("Aucune photo analysée correspondant à l'export.")
    wb = Workbook()
    ws = wb.active
    ws.title = "ChronoPic"
    headers = ["Nom de la photo", "Date du cliché", "Année", "Mois", "Métadonnée",
               "Appareil photo", "Dimensions", "Format", "Statut", "Chemin du fichier"]
    ws.append(headers)
    undated = wb.create_sheet("Photos sans date")
    undated.append(headers)
    for p in analyzed:
        d = p.get("date")
        dims = f'{p.get("largeur")} × {p.get("hauteur")}' if p.get("largeur") and p.get("hauteur") else "Inconnues"
        row = [p["nom"], p.get("date_affichee", "Inconnue"), d.year if d else "",
               d.month if d else "", p.get("source", ""), p.get("appareil", ""),
               dims, p.get("format", ""), p.get("statut", ""), p["chemin"]]
        (ws if d else undated).append(row)
    for sheet in wb.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2878C8", end_color="2878C8", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        widths = [30, 22, 10, 10, 24, 26, 18, 12, 22, 65]
        for i, width in enumerate(widths, 1):
            sheet.column_dimensions[get_column_letter(i)].width = width
    wb.save(path)
