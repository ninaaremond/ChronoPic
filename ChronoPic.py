
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


class ChronoPic:

    def __init__(self, root):
        self.root = root
        self.root.title("ChronoPic - Analyseur de photos")
        self.root.geometry("950x650")
        self.root.minsize(750, 500)

        self.dossier = ""
        self.resultats = []

        self.creer_interface()

    # -------------------------------
    # INTERFACE GRAPHIQUE
    # -------------------------------

    def creer_interface(self):

        titre = tk.Label(
            self.root,
            text="ChronoPic",
            font=("Arial", 24, "bold")
        )
        titre.pack(pady=(15, 0))

        sous_titre = tk.Label(
            self.root,
            text="Analyse et classement chronologique de vos photographies",
            font=("Arial", 10)
        )
        sous_titre.pack(pady=(0, 15))

        # Sélection du dossier
        cadre_dossier = tk.Frame(self.root)
        cadre_dossier.pack(fill="x", padx=20, pady=10)

        self.label_dossier = tk.Label(
            cadre_dossier,
            text="Aucun dossier sélectionné",
            anchor="w",
            relief="sunken",
            padx=8,
            pady=7
        )
        self.label_dossier.pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )

        bouton_parcourir = tk.Button(
            cadre_dossier,
            text="Parcourir",
            command=self.selectionner_dossier
        )
        bouton_parcourir.pack(side="right")

        # Boutons d'action
        cadre_boutons = tk.Frame(self.root)
        cadre_boutons.pack(pady=10)

        self.bouton_analyser = tk.Button(
            cadre_boutons,
            text="Lancer l'analyse",
            command=self.analyser_photos,
            bg="#2878C8",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        )
        self.bouton_analyser.pack(side="left", padx=5)

        self.bouton_exporter = tk.Button(
            cadre_boutons,
            text="Exporter vers Excel",
            command=self.exporter_excel,
            state="disabled",
            padx=15,
            pady=8
        )
        self.bouton_exporter.pack(side="left", padx=5)

        # Statistiques
        self.label_stats = tk.Label(
            self.root,
            text="En attente d'analyse...",
            font=("Arial", 10, "bold")
        )
        self.label_stats.pack(pady=10)

        # Tableau des résultats
        cadre_tableau = tk.Frame(self.root)
        cadre_tableau.pack(
            fill="both", expand=True, padx=20, pady=10
        )

        colonnes = ("photo", "date", "source", "statut")

        self.tableau = ttk.Treeview(
            cadre_tableau,
            columns=colonnes,
            show="headings"
        )

        self.tableau.heading("photo", text="Nom de la photo")
        self.tableau.heading("date", text="Date du cliché")
        self.tableau.heading("source", text="Métadonnée utilisée")
        self.tableau.heading("statut", text="Statut")

        self.tableau.column("photo", width=260)
        self.tableau.column("date", width=150, anchor="center")
        self.tableau.column("source", width=180, anchor="center")
        self.tableau.column("statut", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(
            cadre_tableau,
            orient="vertical",
            command=self.tableau.yview
        )

        self.tableau.configure(yscrollcommand=scrollbar.set)

        self.tableau.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Barre de progression
        self.progression = ttk.Progressbar(
            self.root,
            mode="determinate"
        )
        self.progression.pack(fill="x", padx=20, pady=5)

        self.label_progression = tk.Label(
            self.root,
            text="Prêt",
            font=("Arial", 9)
        )
        self.label_progression.pack(pady=(0, 10))

    # -------------------------------
    # SELECTION DU DOSSIER
    # -------------------------------

    def selectionner_dossier(self):

        dossier = filedialog.askdirectory(
            title="Sélectionner le dossier contenant les photos"
        )

        if dossier:
            self.dossier = dossier
            self.label_dossier.config(text=dossier)

            self.resultats = []
            self.tableau.delete(*self.tableau.get_children())
            self.label_stats.config(text="Dossier sélectionné.")
            self.bouton_exporter.config(state="disabled")

    # -------------------------------
    # LECTURE DES METADONNEES EXIF
    # -------------------------------

    def lire_date_exif(self, chemin):

        try:
            with Image.open(chemin) as image:

                exif = image.getexif()

                # Les dates principales se trouvent dans l'EXIF IFD
                try:
                    exif_detail = exif.get_ifd(0x8769)
                except Exception:
                    exif_detail = {}

                # Priorité à la date réelle de prise de vue
                dates = [
                    (exif_detail.get(36867), "DateTimeOriginal"),
                    (exif_detail.get(36868), "DateTimeDigitized"),
                    (exif.get(306), "DateTime")
                ]

                for valeur, source in dates:

                    if valeur:
                        if isinstance(valeur, bytes):
                            valeur = valeur.decode(
                                "utf-8", errors="replace"
                            )

                        try:
                            date = datetime.strptime(
                                str(valeur).strip(),
                                "%Y:%m:%d %H:%M:%S"
                            )

                            return date, source

                        except ValueError:
                            continue

                return None, "Aucune date EXIF"

        except Exception:
            return None, "Erreur de lecture"

    # -------------------------------
    # ANALYSE DES PHOTOS
    # -------------------------------

    def analyser_photos(self):

        if not self.dossier:
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner un dossier."
            )
            return

        extensions = (
            ".jpg", ".jpeg", ".tif", ".tiff", ".png"
        )

        fichiers = [
            f for f in os.listdir(self.dossier)
            if os.path.isfile(os.path.join(self.dossier, f))
            and f.lower().endswith(extensions)
        ]

        if not fichiers:
            messagebox.showinfo(
                "Information",
                "Aucune photo compatible trouvée."
            )
            return

        self.tableau.delete(*self.tableau.get_children())
        self.resultats = []

        self.bouton_analyser.config(state="disabled")
        self.bouton_exporter.config(state="disabled")

        self.progression["maximum"] = len(fichiers)
        self.progression["value"] = 0

        total = len(fichiers)

        for index, fichier in enumerate(fichiers, start=1):

            chemin = os.path.join(self.dossier, fichier)

            date, source = self.lire_date_exif(chemin)

            if date:
                date_affichee = date.strftime("%d/%m/%Y %H:%M:%S")
                statut = "Date trouvée"
            else:
                date_affichee = "Inconnue"
                statut = source

            self.resultats.append({
                "photo": fichier,
                "date": date,
                "date_affichee": date_affichee,
                "source": source,
                "statut": statut,
                "chemin": chemin
            })

            self.progression["value"] = index
            self.label_progression.config(
                text=f"Analyse : {index}/{total} photos"
            )

            self.root.update_idletasks()

        # Tri chronologique : les dates inconnues à la fin
        self.resultats.sort(
            key=lambda x: (
                x["date"] is None,
                x["date"] or datetime.max
            )
        )

        for resultat in self.resultats:

            self.tableau.insert(
                "",
                "end",
                values=(
                    resultat["photo"],
                    resultat["date_affichee"],
                    resultat["source"],
                    resultat["statut"]
                )
            )

        trouvees = sum(
            1 for r in self.resultats if r["date"] is not None
        )

        inconnues = total - trouvees

        self.label_stats.config(
            text=(
                f"{total} photos analysées | "
                f"{trouvees} dates trouvées | "
                f"{inconnues} sans date"
            )
        )

        self.label_progression.config(text="Analyse terminée.")

        self.bouton_analyser.config(state="normal")
        self.bouton_exporter.config(state="normal")

    # -------------------------------
    # EXPORT EXCEL
    # -------------------------------

    def exporter_excel(self):

        if not self.resultats:
            return

        chemin = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")],
            initialfile="ChronoPic_Resultats.xlsx"
        )

        if not chemin:
            return

        try:
            classeur = Workbook()
            feuille = classeur.active
            feuille.title = "ChronoPic"

            entetes = [
                "Nom de la photo",
                "Date du cliché",
                "Métadonnée",
                "Statut",
                "Chemin du fichier"
            ]

            feuille.append(entetes)

            for cellule in feuille[1]:
                cellule.font = Font(bold=True, color="FFFFFF")
                cellule.fill = PatternFill(
                    start_color="2878C8",
                    end_color="2878C8",
                    fill_type="solid"
                )
                cellule.alignment = Alignment(horizontal="center")

            for r in self.resultats:

                feuille.append([
                    r["photo"],
                    r["date_affichee"],
                    r["source"],
                    r["statut"],
                    r["chemin"]
                ])

            feuille.freeze_panes = "A2"
            feuille.auto_filter.ref = feuille.dimensions

            largeurs = {
                "A": 30,
                "B": 22,
                "C": 25,
                "D": 22,
                "E": 75
            }

            for colonne, largeur in largeurs.items():
                feuille.column_dimensions[colonne].width = largeur

            classeur.save(chemin)

            messagebox.showinfo(
                "Export réussi",
                f"Fichier Excel créé avec succès :\n{chemin}"
            )

        except Exception as erreur:
            messagebox.showerror(
                "Erreur",
                f"Impossible de créer le fichier Excel :\n{erreur}"
            )


# -------------------------------
# DEMARRAGE DE L'APPLICATION
# -------------------------------

if __name__ == "__main__":

    root = tk.Tk()
    application = ChronoPic(root)
    root.mainloop()
