
import os
import tkinter as tk
import threading
import queue
import io

from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from config import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WIDTH,
    MIN_HEIGHT,
    PHOTOS_PER_PAGE,
    GALLERY_COLUMNS,
    COLOR_PRIMARY,
    COLOR_BACKGROUND,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_ERROR
)

from photo_manager import PhotoManager
from exif_reader import read_photo_date, format_photo_date
from thumbnail import create_thumbnail, create_preview
from excel_export import export_to_excel


class ChronoPicInterface:

    def __init__(self, root):

        self.root = root

        self.root.title(
            f"{APP_NAME} - Version {APP_VERSION}"
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            MIN_WIDTH,
            MIN_HEIGHT
        )

        self.manager = PhotoManager()

        self.queue = queue.Queue()

        self.analyse_en_cours = False
        self.generation = 0
        self.page = 0

        self.thumbnail_cancel = threading.Event()

        self.images = []
        self.variables = {}

        self.creer_interface()

        self.root.after(
            50,
            self.traiter_queue
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.fermer
        )

    # ==========================================
    # INTERFACE
    # ==========================================

    def creer_interface(self):

        tk.Label(
            self.root,
            text=APP_NAME,
            font=("Arial", 26, "bold"),
            fg=COLOR_PRIMARY
        ).pack(pady=(15, 0))

        tk.Label(
            self.root,
            text="Gestion et classement chronologique de vos photographies",
            font=("Arial", 10)
        ).pack(pady=(0, 15))

        # Boutons de sélection
        selection = tk.Frame(self.root)
        selection.pack(fill="x", padx=20)

        self.btn_dossier = tk.Button(
            selection,
            text="Sélectionner un dossier",
            command=self.selectionner_dossier
        )

        self.btn_dossier.pack(side="left", padx=5)

        self.btn_photos = tk.Button(
            selection,
            text="Ajouter des photos",
            command=self.selectionner_photos
        )

        self.btn_photos.pack(side="left", padx=5)

        self.btn_effacer = tk.Button(
            selection,
            text="Tout effacer",
            command=self.effacer_photos
        )

        self.btn_effacer.pack(side="left", padx=5)

        # Boutons d'analyse
        actions = tk.Frame(self.root)
        actions.pack(fill="x", padx=20, pady=12)

        self.btn_analyser = tk.Button(
            actions,
            text="Analyser la sélection",
            command=self.analyser_selection,
            bg=COLOR_PRIMARY,
            fg="white",
            padx=12,
            pady=7
        )

        self.btn_analyser.pack(side="left", padx=5)

        self.btn_tout = tk.Button(
            actions,
            text="Analyser toutes les photos",
            command=self.analyser_tout,
            padx=12,
            pady=7
        )

        self.btn_tout.pack(side="left", padx=5)

        self.btn_excel = tk.Button(
            actions,
            text="Exporter Excel",
            command=self.exporter_excel,
            state="disabled",
            padx=12,
            pady=7
        )

        self.btn_excel.pack(side="left", padx=5)

        # Statistiques
        self.label_stats = tk.Label(
            self.root,
            text="Aucune photo chargée",
            font=("Arial", 10, "bold")
        )

        self.label_stats.pack(pady=5)

        # Sélection globale
        global_frame = tk.Frame(self.root)
        global_frame.pack(fill="x", padx=20)

        tk.Button(
            global_frame,
            text="Tout sélectionner",
            command=lambda: self.selection_globale(True)
        ).pack(side="left", padx=5)

        tk.Button(
            global_frame,
            text="Tout désélectionner",
            command=lambda: self.selection_globale(False)
        ).pack(side="left", padx=5)

        # Galerie
        galerie = tk.Frame(self.root)
        galerie.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.canvas = tk.Canvas(
            galerie,
            bg=COLOR_BACKGROUND,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            galerie,
            orient="vertical",
            command=self.canvas.yview
        )

        self.frame_galerie = tk.Frame(
            self.canvas,
            bg=COLOR_BACKGROUND
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.frame_galerie,
            anchor="nw"
        )

        self.frame_galerie.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.window_id,
                width=e.width
            )
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.defiler
        )

        # Pagination
        pagination = tk.Frame(self.root)
        pagination.pack(pady=5)

        self.btn_precedent = tk.Button(
            pagination,
            text="<< Précédent",
            command=self.page_precedente
        )

        self.btn_precedent.pack(side="left", padx=10)

        self.label_page = tk.Label(
            pagination,
            text="Page 0 / 0"
        )

        self.label_page.pack(side="left", padx=10)

        self.btn_suivant = tk.Button(
            pagination,
            text="Suivant >>",
            command=self.page_suivante
        )

        self.btn_suivant.pack(side="left", padx=10)

        # Progression
        self.progression = ttk.Progressbar(
            self.root,
            mode="determinate"
        )

        self.progression.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.label_progression = tk.Label(
            self.root,
            text="Prêt"
        )

        self.label_progression.pack(
            pady=(0, 10)
        )

    # ==========================================
    # DEFILEMENT
    # ==========================================

    def defiler(self, event):

        self.canvas.yview_scroll(
            int(-1 * event.delta / 120),
            "units"
        )

    # ==========================================
    # SELECTION
    # ==========================================

    def selectionner_dossier(self):

        if self.analyse_en_cours:
            return

        dossier = filedialog.askdirectory()

        if not dossier:
            return

        self.manager.clear()

        self.manager.load_folder(dossier)

        self.page = 0

        self.btn_excel.config(state="disabled")

        self.afficher_galerie()

        self.label_progression.config(
            text="Dossier chargé."
        )

    def selectionner_photos(self):

        if self.analyse_en_cours:
            return

        files = filedialog.askopenfilenames(
            title="Sélectionner des photos",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp"),
                ("Tous les fichiers", "*.*")
            ]
        )

        if not files:
            return

        self.manager.add_photos(files)

        self.afficher_galerie()

        self.label_progression.config(
            text="Photos ajoutées."
        )

    def effacer_photos(self):

        if self.analyse_en_cours:
            return

        self.thumbnail_cancel.set()

        self.manager.clear()

        self.page = 0

        self.btn_excel.config(state="disabled")

        self.afficher_galerie()

        self.label_progression.config(
            text="Prêt"
        )

    # ==========================================
    # ANALYSE EN ARRIERE-PLAN
    # ==========================================

    def analyser_selection(self):

        photos = self.manager.get_selected()

        self.lancer_analyse(photos)

    def analyser_tout(self):

        self.lancer_analyse(
            self.manager.photos
        )

    def lancer_analyse(self, photos):

        if self.analyse_en_cours:
            return

        if not photos:

            messagebox.showwarning(
                "Attention",
                "Aucune photo à analyser."
            )

            return

        self.analyse_en_cours = True

        self.boutons_etat("disabled")

        self.progression["value"] = 0
        self.progression["maximum"] = len(photos)

        self.label_progression.config(
            text="Analyse en cours..."
        )

        def travail():

            for index, photo in enumerate(photos, start=1):

                date, source = read_photo_date(
                    photo["chemin"]
                )

                self.queue.put((
                    "resultat",
                    photo,
                    date,
                    source,
                    index
                ))

            self.queue.put(("termine",))

        threading.Thread(
            target=travail,
            daemon=True
        ).start()

    def boutons_etat(self, etat):

        self.btn_dossier.config(state=etat)
        self.btn_photos.config(state=etat)
        self.btn_effacer.config(state=etat)
        self.btn_analyser.config(state=etat)
        self.btn_tout.config(state=etat)

    # ==========================================
    # QUEUE
    # ==========================================

    def traiter_queue(self):

        try:

            while True:

                event = self.queue.get_nowait()

                if event[0] == "resultat":

                    _, photo, date, source, index = event

                    photo["date"] = date
                    photo["source"] = source

                    if date:

                        photo["date_affichee"] = format_photo_date(date)

                        photo["statut"] = "Date trouvée"

                    else:

                        photo["date_affichee"] = "Inconnue"
                        photo["statut"] = source

                    self.progression["value"] = index

                    self.label_progression.config(
                        text=f"Analyse : {index}/{int(self.progression['maximum'])}"
                    )

                elif event[0] == "miniature":

                    _, generation, index, data = event

                    if generation == self.generation:

                        self.afficher_miniature(
                            index,
                            data
                        )

                elif event[0] == "termine":

                    self.analyse_en_cours = False

                    self.boutons_etat("normal")

                    self.manager.sort_chronologically()

                    self.page = 0

                    self.afficher_galerie()

                    self.btn_excel.config(
                        state="normal"
                    )

                    self.label_progression.config(
                        text="Analyse terminée."
                    )

        except queue.Empty:
            pass

        self.actualiser_stats()

        self.root.after(
            50,
            self.traiter_queue
        )

    # ==========================================
    # MINIATURES
    # ==========================================

    def charger_miniatures(self, photos, generation):

        self.thumbnail_cancel.set()

        self.thumbnail_cancel = threading.Event()

        cancel_event = self.thumbnail_cancel

        def travail():

            for index, photo in photos:

                if cancel_event.is_set():
                    break

                data = create_thumbnail(
                    photo["chemin"]
                )

                if cancel_event.is_set():
                    break

                self.queue.put((
                    "miniature",
                    generation,
                    index,
                    data
                ))

        threading.Thread(
            target=travail,
            daemon=True
        ).start()

    def afficher_miniature(self, index, data):

        if index not in self.variables:
            return

        label = self.variables[index]["image"]

        if data is None:

            label.config(
                text="Aperçu indisponible"
            )

            return

        try:

            image = Image.open(
                io.BytesIO(data)
            )

            photo_image = ImageTk.PhotoImage(image)

            self.images.append(photo_image)

            label.config(
                image=photo_image,
                text=""
            )

        except Exception:

            label.config(
                text="Aperçu indisponible"
            )

    # ==========================================
    # GALERIE
    # ==========================================

    def afficher_galerie(self):

        self.generation += 1

        generation = self.generation

        self.thumbnail_cancel.set()

        for widget in self.frame_galerie.winfo_children():
            widget.destroy()

        self.images = []
        self.variables = {}

        debut = self.page * PHOTOS_PER_PAGE
        fin = debut + PHOTOS_PER_PAGE

        page_photos = self.manager.photos[debut:fin]

        for index, photo in enumerate(page_photos, start=debut):

            ligne = (index - debut) // GALLERY_COLUMNS
            colonne = (index - debut) % GALLERY_COLUMNS

            carte = tk.Frame(
                self.frame_galerie,
                bg="white",
                bd=1,
                relief="solid",
                padx=8,
                pady=8
            )

            carte.grid(
                row=ligne,
                column=colonne,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            
            # Zone d'affichage des miniatures
            label_image = tk.Label(
                carte,
                text="Chargement...",
                width=200,
                height=150,
                bg="#EEEEEE",
                cursor="hand2",
                anchor="center"
            )

            label_image.pack(pady=5)


            label_image.bind(
                "<Button-1>",
                lambda e, p=photo: self.ouvrir_apercu(p)
            )

            tk.Label(
                carte,
                text=photo["nom"],
                bg="white",
                wraplength=180,
                font=("Arial", 9, "bold")
            ).pack(pady=3)

            tk.Label(
                carte,
                text=photo["date_affichee"],
                bg="white",
                fg=COLOR_PRIMARY
            ).pack()

            variable = tk.BooleanVar(
                value=photo["selection"]
            )

            def modifier_selection(p=photo, v=variable):

                p["selection"] = v.get()

                self.actualiser_stats()

            tk.Checkbutton(
                carte,
                text="Sélectionner",
                variable=variable,
                command=modifier_selection,
                bg="white"
            ).pack(pady=3)

            self.variables[index] = {
                "image": label_image
            }

        for colonne in range(GALLERY_COLUMNS):

            self.frame_galerie.columnconfigure(
                colonne,
                weight=1
            )

        total = len(self.manager.photos)

        total_pages = max(
            1,
            (total + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE
        )

        self.label_page.config(
            text=f"Page {self.page + 1} / {total_pages}"
        )

        self.btn_precedent.config(
            state="normal" if self.page > 0 else "disabled"
        )

        self.btn_suivant.config(
            state=(
                "normal"
                if self.page < total_pages - 1
                else "disabled"
            )
        )

        self.canvas.yview_moveto(0)

        liste = [
            (index, self.manager.photos[index])
            for index in range(debut, min(fin, total))
        ]

        self.charger_miniatures(
            liste,
            generation
        )

        self.actualiser_stats()

    # ==========================================
    # PAGINATION
    # ==========================================

    def page_precedente(self):

        if self.page > 0:

            self.page -= 1

            self.afficher_galerie()

    def page_suivante(self):

        total_pages = (
            len(self.manager.photos) + PHOTOS_PER_PAGE - 1
        ) // PHOTOS_PER_PAGE

        if self.page < total_pages - 1:

            self.page += 1

            self.afficher_galerie()

    # ==========================================
    # APERCU GRAND FORMAT
    # ==========================================

    def ouvrir_apercu(self, photo):

        fenetre = tk.Toplevel(self.root)

        fenetre.title(photo["nom"])

        fenetre.geometry("900x700")

        fenetre.configure(bg="#222222")

        try:

            image = create_preview(
                photo["chemin"]
            )

            if image is None:
                raise ValueError("Impossible de lire cette photo.")

            apercu = ImageTk.PhotoImage(image)

            label = tk.Label(
                fenetre,
                image=apercu,
                bg="#222222"
            )

            label.image = apercu

            label.pack(pady=15)

            tk.Label(
                fenetre,
                text=photo["nom"],
                font=("Arial", 12, "bold"),
                fg="white",
                bg="#222222"
            ).pack()

            tk.Label(
                fenetre,
                text=f"Date : {photo['date_affichee']}",
                fg="white",
                bg="#222222"
            ).pack(pady=5)

            tk.Label(
                fenetre,
                text=f"Métadonnée : {photo['source']}",
                fg="white",
                bg="#222222"
            ).pack()

        except Exception as erreur:

            fenetre.destroy()

            messagebox.showerror(
                "Erreur",
                str(erreur)
            )

    # ==========================================
    # SELECTION GLOBALE
    # ==========================================

    def selection_globale(self, value):

        self.manager.select_all(value)

        self.afficher_galerie()

    # ==========================================
    # STATISTIQUES
    # ==========================================

    def actualiser_stats(self):

        total = self.manager.get_count()

        selection = len(
            self.manager.get_selected()
        )

        dates = self.manager.get_dated_count()

        sans_date = self.manager.get_undated_count()

        self.label_stats.config(
            text=(
                f"{total} photos | "
                f"{selection} sélectionnées | "
                f"{dates} dates trouvées | "
                f"{sans_date} sans date"
            )
        )

    # ==========================================
    # EXPORT EXCEL
    # ==========================================

    def exporter_excel(self):

        if self.manager.get_analyzed_count() == 0:

            messagebox.showwarning(
                "Attention",
                "Aucune photo analysée."
            )

            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Fichier Excel", "*.xlsx")
            ],
            initialfile="ChronoPic_Resultats.xlsx"
        )

        if not path:
            return

        try:

            export_to_excel(
                self.manager.photos,
                path
            )

            messagebox.showinfo(
                "Export réussi",
                f"Fichier créé :\n{path}"
            )

        except Exception as erreur:

            messagebox.showerror(
                "Erreur",
                str(erreur)
            )

    # ==========================================
    # FERMETURE
    # ==========================================

    def fermer(self):

        self.thumbnail_cancel.set()

        self.generation += 1

        self.root.destroy()
