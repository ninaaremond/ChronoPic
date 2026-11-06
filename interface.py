
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import io

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
    COLOR_WARNING
)

from photo_manager import PhotoManager
from exif_reader import read_photo_date, format_photo_date
from thumbnail import create_thumbnail, create_preview
from excel_export import export_to_excel


class ChronoPicInterface:

    # Palette graphique
    BG = "#F3F5F9"
    WHITE = "#FFFFFF"
    DARK = "#202B3C"
    SECONDARY = "#748094"
    BORDER = "#E5E9F0"
    BLUE = "#3978DB"
    BLUE_LIGHT = "#EAF1FE"
    GREEN = "#20865B"
    ORANGE = "#C78327"

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

        self.root.configure(bg=self.BG)

        self.manager = PhotoManager()
        self.queue = queue.Queue()

        self.analyse_en_cours = False
        self.generation = 0
        self.page = 0

        self.thumbnail_cancel = threading.Event()

        self.images = []
        self.variables = {}

        self.creer_styles()
        self.creer_interface()

        self.root.after(50, self.traiter_queue)
        self.root.protocol("WM_DELETE_WINDOW", self.fermer)

    # ==========================================
    # STYLES
    # ==========================================

    def creer_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Chrono.Horizontal.TProgressbar",
            troughcolor="#E5EAF2",
            background=self.BLUE,
            bordercolor="#E5EAF2",
            lightcolor=self.BLUE,
            darkcolor=self.BLUE,
            thickness=9
        )

        style.configure(
            "Chrono.Vertical.TScrollbar",
            background="#D7DDE7",
            troughcolor=self.BG,
            bordercolor=self.BG,
            arrowcolor=self.SECONDARY
        )

        style.configure(
            "Chrono.TCheckbutton",
            background=self.WHITE,
            foreground=self.DARK,
            font=("Segoe UI", 9)
        )

    # ==========================================
    # PETITS COMPOSANTS GRAPHIQUES
    # ==========================================

    def creer_bouton(
        self,
        parent,
        texte,
        commande,
        principal=False,
        width=None
    ):

        bouton = tk.Button(
            parent,
            text=texte,
            command=commande,
            font=("Segoe UI", 9, "bold"),
            bg=self.BLUE if principal else self.WHITE,
            fg=self.WHITE if principal else self.DARK,
            activebackground="#2863BC" if principal else "#EDF1F7",
            activeforeground=self.WHITE if principal else self.DARK,
            relief="flat",
            bd=0,
            padx=16,
            pady=10,
            cursor="hand2",
            width=width
        )

        return bouton

    def creer_carte_statistique(
        self,
        parent,
        titre,
        valeur,
        couleur
    ):

        carte = tk.Frame(
            parent,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        tk.Label(
            carte,
            text=titre,
            font=("Segoe UI", 9),
            fg=self.SECONDARY,
            bg=self.WHITE
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 3)
        )

        valeur_label = tk.Label(
            carte,
            text=str(valeur),
            font=("Segoe UI", 21, "bold"),
            fg=couleur,
            bg=self.WHITE
        )

        valeur_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

        return carte, valeur_label

    # ==========================================
    # INTERFACE PRINCIPALE
    # ==========================================

    def creer_interface(self):

        # Conteneur principal
        principal = tk.Frame(
            self.root,
            bg=self.BG
        )

        principal.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=18
        )

        # --------------------------------------
        # EN-TETE
        # --------------------------------------

        header = tk.Frame(
            principal,
            bg=self.BG
        )

        header.pack(
            fill="x",
            pady=(0, 18)
        )

        header_gauche = tk.Frame(
            header,
            bg=self.BG
        )

        header_gauche.pack(side="left")

        tk.Label(
            header_gauche,
            text="ChronoPic",
            font=("Segoe UI", 25, "bold"),
            fg=self.DARK,
            bg=self.BG
        ).pack(anchor="w")

        tk.Label(
            header_gauche,
            text="Votre bibliothèque photographique chronologique",
            font=("Segoe UI", 10),
            fg=self.SECONDARY,
            bg=self.BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"VERSION {APP_VERSION}",
            font=("Segoe UI", 8, "bold"),
            fg=self.BLUE,
            bg=self.BLUE_LIGHT,
            padx=12,
            pady=7
        ).pack(side="right", pady=8)

        # --------------------------------------
        # ZONE D'IMPORTATION
        # --------------------------------------

        import_card = tk.Frame(
            principal,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        import_card.pack(
            fill="x",
            pady=(0, 14)
        )

        import_content = tk.Frame(
            import_card,
            bg=self.WHITE
        )

        import_content.pack(
            fill="x",
            padx=18,
            pady=16
        )

        import_gauche = tk.Frame(
            import_content,
            bg=self.WHITE
        )

        import_gauche.pack(
            side="left",
            fill="y"
        )

        tk.Label(
            import_gauche,
            text="Importer vos photographies",
            font=("Segoe UI", 12, "bold"),
            fg=self.DARK,
            bg=self.WHITE
        ).pack(anchor="w")

        tk.Label(
            import_gauche,
            text="Les dates EXIF seront analysées automatiquement.",
            font=("Segoe UI", 9),
            fg=self.SECONDARY,
            bg=self.WHITE
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        import_droite = tk.Frame(
            import_content,
            bg=self.WHITE
        )

        import_droite.pack(
            side="right"
        )

        self.btn_dossier = self.creer_bouton(
            import_droite,
            "📁  Ouvrir un dossier",
            self.selectionner_dossier,
            principal=True
        )

        self.btn_dossier.pack(
            side="left",
            padx=4
        )

        self.btn_photos = self.creer_bouton(
            import_droite,
            "＋  Ajouter des photos",
            self.selectionner_photos
        )

        self.btn_photos.pack(
            side="left",
            padx=4
        )

        self.btn_effacer = self.creer_bouton(
            import_droite,
            "Vider",
            self.effacer_photos
        )

        self.btn_effacer.pack(
            side="left",
            padx=4
        )

        # --------------------------------------
        # STATISTIQUES
        # --------------------------------------

        stats = tk.Frame(
            principal,
            bg=self.BG
        )

        stats.pack(
            fill="x",
            pady=(0, 14)
        )

        stats.columnconfigure(
            (0, 1, 2),
            weight=1
        )

        carte, self.stat_total = self.creer_carte_statistique(
            stats,
            "PHOTOGRAPHIES",
            0,
            self.BLUE
        )

        carte.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 7)
        )

        carte, self.stat_dates = self.creer_carte_statistique(
            stats,
            "DATES IDENTIFIÉES",
            0,
            self.GREEN
        )

        carte.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=7
        )

        carte, self.stat_inconnues = self.creer_carte_statistique(
            stats,
            "DATES INCONNUES",
            0,
            self.ORANGE
        )

        carte.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=(7, 0)
        )

        # --------------------------------------
        # BARRE D'OUTILS DE LA GALERIE
        # --------------------------------------

        toolbar = tk.Frame(
            principal,
            bg=self.BG
        )

        toolbar.pack(
            fill="x",
            pady=(0, 9)
        )

        tk.Label(
            toolbar,
            text="Votre galerie",
            font=("Segoe UI", 14, "bold"),
            fg=self.DARK,
            bg=self.BG
        ).pack(side="left")

        self.label_compteur = tk.Label(
            toolbar,
            text="0 photo",
            font=("Segoe UI", 9),
            fg=self.SECONDARY,
            bg=self.BG
        )

        self.label_compteur.pack(
            side="left",
            padx=12
        )

        self.btn_excel = self.creer_bouton(
            toolbar,
            "↓  Exporter vers Excel",
            self.exporter_excel,
            principal=True
        )

        self.btn_excel.pack(side="right")

        # --------------------------------------
        # GALERIE
        # --------------------------------------

        galerie_card = tk.Frame(
            principal,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        galerie_card.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            galerie_card,
            bg=self.WHITE,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            galerie_card,
            orient="vertical",
            command=self.canvas.yview,
            style="Chrono.Vertical.TScrollbar"
        )

        self.frame_galerie = tk.Frame(
            self.canvas,
            bg=self.WHITE
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
            expand=True,
            padx=(12, 0),
            pady=12
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 5),
            pady=8
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.defiler
        )

        # --------------------------------------
        # PAGINATION
        # --------------------------------------

        pagination = tk.Frame(
            principal,
            bg=self.BG
        )

        pagination.pack(
            fill="x",
            pady=(10, 5)
        )

        self.btn_precedent = self.creer_bouton(
            pagination,
            "← Précédent",
            self.page_precedente
        )

        self.btn_precedent.pack(side="left")

        self.label_page = tk.Label(
            pagination,
            text="Page 0 / 0",
            font=("Segoe UI", 9, "bold"),
            fg=self.SECONDARY,
            bg=self.BG
        )

        self.label_page.pack(
            side="left",
            expand=True
        )

        self.btn_suivant = self.creer_bouton(
            pagination,
            "Suivant →",
            self.page_suivante
        )

        self.btn_suivant.pack(side="right")

        # --------------------------------------
        # STATUT ET PROGRESSION
        # --------------------------------------

        footer = tk.Frame(
            principal,
            bg=self.BG
        )

        footer.pack(
            fill="x",
            pady=(5, 0)
        )

        self.label_analyse = tk.Label(
            footer,
            text="●  En attente de photographies",
            font=("Segoe UI", 9),
            fg=self.SECONDARY,
            bg=self.BG
        )

        self.label_analyse.pack(
            anchor="w",
            pady=(0, 5)
        )

        self.progression = ttk.Progressbar(
            footer,
            mode="determinate",
            style="Chrono.Horizontal.TProgressbar"
        )

        self.progression.pack(
            fill="x"
        )

        self.label_progression = tk.Label(
            footer,
            text="Prêt à importer vos photos",
            font=("Segoe UI", 8),
            fg=self.SECONDARY,
            bg=self.BG
        )

        self.label_progression.pack(
            anchor="w",
            pady=(4, 0)
        )

        self.actualiser_stats()

    # ==========================================
    # DEFILEMENT
    # ==========================================

    def defiler(self, event):

        self.canvas.yview_scroll(
            int(-1 * event.delta / 120),
            "units"
        )

    # ==========================================
    # SELECTION D'UN DOSSIER
    # ==========================================

    def selectionner_dossier(self):

        if self.analyse_en_cours:
            return

        dossier = filedialog.askdirectory(
            title="Sélectionner un dossier de photos"
        )

        if not dossier:
            return

        self.thumbnail_cancel.set()

        self.manager.clear()

        nombre = self.manager.load_folder(dossier)

        self.page = 0

        self.btn_excel.config(
            state="disabled"
        )

        self.afficher_galerie()

        if self.manager.photos:

            self.label_analyse.config(
                text="●  Analyse EXIF en cours...",
                fg=self.ORANGE
            )

            self.lancer_analyse(
                self.manager.photos.copy()
            )

        else:

            self.label_analyse.config(
                text="●  Aucune photographie trouvée",
                fg=self.ORANGE
            )

            self.label_progression.config(
                text="Le dossier sélectionné ne contient aucune image compatible."
            )

        self.actualiser_stats()

    # ==========================================
    # SELECTION INDIVIDUELLE
    # ==========================================

    def selectionner_photos(self):

        if self.analyse_en_cours:
            return

        files = filedialog.askopenfilenames(
            title="Sélectionner des photographies",
            filetypes=[
                (
                    "Images",
                    "*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp"
                ),
                ("Tous les fichiers", "*.*")
            ]
        )

        if not files:
            return

        chemins_existants = {
            photo["chemin"]
            for photo in self.manager.photos
        }

        nombre = self.manager.add_photos(files)

        nouvelles_photos = [
            photo
            for photo in self.manager.photos
            if photo["chemin"] not in chemins_existants
        ]

        if not nouvelles_photos:

            messagebox.showinfo(
                "Information",
                "Ces photographies sont déjà présentes dans la galerie."
            )

            return

        self.page = 0

        self.afficher_galerie()

        self.label_analyse.config(
            text="●  Analyse EXIF en cours...",
            fg=self.ORANGE
        )

        self.lancer_analyse(
            nouvelles_photos
        )

    # ==========================================
    # EFFACER LA GALERIE
    # ==========================================

    def effacer_photos(self):

        if self.analyse_en_cours:
            return

        self.thumbnail_cancel.set()

        self.manager.clear()

        self.page = 0

        self.btn_excel.config(
            state="disabled"
        )

        self.progression["value"] = 0

        self.label_progression.config(
            text="Prêt à importer vos photos"
        )

        self.label_analyse.config(
            text="●  En attente de photographies",
            fg=self.SECONDARY
        )

        self.afficher_galerie()

    # ==========================================
    # ANALYSE AUTOMATIQUE EN ARRIERE-PLAN
    # ==========================================

    def lancer_analyse(self, photos):

        if self.analyse_en_cours or not photos:
            return

        self.analyse_en_cours = True

        self.boutons_etat("disabled")

        self.btn_excel.config(
            state="disabled"
        )

        self.progression["value"] = 0
        self.progression["maximum"] = len(photos)

        self.label_analyse.config(
            text="●  Analyse EXIF en cours...",
            fg=self.ORANGE
        )

        self.label_progression.config(
            text=f"Analyse de {len(photos)} photographie(s)..."
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

            self.queue.put((
                "termine",
                len(photos)
            ))

        threading.Thread(
            target=travail,
            daemon=True
        ).start()

    # ==========================================
    # ETAT DES BOUTONS
    # ==========================================

    def boutons_etat(self, etat):

        self.btn_dossier.config(state=etat)
        self.btn_photos.config(state=etat)
        self.btn_effacer.config(state=etat)

    # ==========================================
    # TRAITEMENT DES MESSAGES
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

                    total = int(
                        self.progression["maximum"]
                    )

                    self.label_progression.config(
                        text=f"Analyse des métadonnées : {index}/{total}"
                    )

                    self.actualiser_stats()

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

                    if self.manager.get_analyzed_count() > 0:

                        self.btn_excel.config(
                            state="normal"
                        )

                    self.label_analyse.config(
                        text="●  Analyse terminée",
                        fg=self.GREEN
                    )

                    self.label_progression.config(
                        text=f"{event[1]} photographie(s) analysée(s)."
                    )

                    self.actualiser_stats()

        except queue.Empty:
            pass

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

            photo_image = ImageTk.PhotoImage(
                image
            )

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
    # GALERIE PHOTOGRAPHIQUE
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

        if not self.manager.photos:

            self.afficher_galerie_vide()
            self.actualiser_stats()
            return

        for index, photo in enumerate(page_photos, start=debut):

            ligne = (index - debut) // GALLERY_COLUMNS
            colonne = (index - debut) % GALLERY_COLUMNS

            # Carte individuelle
            carte = tk.Frame(
                self.frame_galerie,
                bg=self.WHITE,
                highlightbackground=self.BORDER,
                highlightthickness=1,
                padx=9,
                pady=9
            )

            carte.grid(
                row=ligne,
                column=colonne,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            # Miniature
            label_image = tk.Label(
                carte,
                text="Chargement...",
                width=200,
                height=150,
                bg="#EDF0F5",
                cursor="hand2",
                anchor="center"
            )

            label_image.pack(
                pady=(0, 9)
            )

            label_image.bind(
                "<Button-1>",
                lambda e, p=photo: self.ouvrir_apercu(p)
            )

            # Nom de fichier
            tk.Label(
                carte,
                text=photo["nom"],
                font=("Segoe UI", 9, "bold"),
                fg=self.DARK,
                bg=self.WHITE,
                wraplength=190,
                justify="left"
            ).pack(
                anchor="w",
                pady=(0, 5)
            )

            # Date
            label_date = tk.Label(
                carte,
                text=photo["date_affichee"],
                font=("Segoe UI", 8),
                fg=self.BLUE,
                bg=self.WHITE
            )

            label_date.pack(
                anchor="w"
            )

            # Sélection individuelle
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
                font=("Segoe UI", 8),
                fg=self.SECONDARY,
                bg=self.WHITE,
                activebackground=self.WHITE,
                selectcolor=self.WHITE,
                relief="flat",
                bd=0
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

            self.variables[index] = {
                "image": label_image,
                "date": label_date
            }

        # Colonnes adaptatives
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

        self.label_compteur.config(
            text=f"{total} photographie(s)"
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
    # GALERIE VIDE
    # ==========================================

    def afficher_galerie_vide(self):

        empty = tk.Frame(
            self.frame_galerie,
            bg=self.WHITE
        )

        empty.pack(
            expand=True,
            fill="both",
            pady=100
        )

        tk.Label(
            empty,
            text="📷",
            font=("Segoe UI Emoji", 38),
            bg=self.WHITE
        ).pack(pady=8)

        tk.Label(
            empty,
            text="Votre galerie est vide",
            font=("Segoe UI", 15, "bold"),
            fg=self.DARK,
            bg=self.WHITE
        ).pack()

        tk.Label(
            empty,
            text="Commencez par sélectionner un dossier ou ajouter des photos.",
            font=("Segoe UI", 9),
            fg=self.SECONDARY,
            bg=self.WHITE
        ).pack(pady=8)

        self.label_page.config(
            text="Page 0 / 0"
        )

        self.btn_precedent.config(
            state="disabled"
        )

        self.btn_suivant.config(
            state="disabled"
        )

        self.label_compteur.config(
            text="0 photographie"
        )

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

        fenetre.configure(
            bg="#202B3C"
        )

        try:

            image = create_preview(
                photo["chemin"]
            )

            if image is None:

                raise ValueError(
                    "Impossible de lire cette photo."
                )

            apercu = ImageTk.PhotoImage(
                image
            )

            label = tk.Label(
                fenetre,
                image=apercu,
                bg="#202B3C"
            )

            label.image = apercu

            label.pack(
                pady=20
            )

            tk.Label(
                fenetre,
                text=photo["nom"],
                font=("Segoe UI", 13, "bold"),
                fg="white",
                bg="#202B3C"
            ).pack()

            tk.Label(
                fenetre,
                text=f"Date du cliché : {photo['date_affichee']}",
                font=("Segoe UI", 10),
                fg="#D7E0EF",
                bg="#202B3C"
            ).pack(pady=7)

            tk.Label(
                fenetre,
                text=f"Métadonnée : {photo['source']}",
                font=("Segoe UI", 9),
                fg="#AEBBD0",
                bg="#202B3C"
            ).pack()

        except Exception as erreur:

            fenetre.destroy()

            messagebox.showerror(
                "Erreur",
                f"Impossible d'ouvrir cette photo :\n{erreur}"
            )

    # ==========================================
    # STATISTIQUES
    # ==========================================

    def actualiser_stats(self):

        total = self.manager.get_count()

        dates = self.manager.get_dated_count()

        inconnues = self.manager.get_undated_count()

        selection = len(
            self.manager.get_selected()
        )

        self.stat_total.config(
            text=str(total)
        )

        self.stat_dates.config(
            text=str(dates)
        )

        self.stat_inconnues.config(
            text=str(inconnues)
        )

        self.label_compteur.config(
            text=f"{total} photographie(s) · {selection} sélectionnée(s)"
        )

    # ==========================================
    # EXPORT EXCEL
    # ==========================================

    def exporter_excel(self):

        if self.analyse_en_cours:

            messagebox.showinfo(
                "Analyse en cours",
                "Veuillez attendre la fin de l'analyse avant l'export."
            )

            return

        if self.manager.get_analyzed_count() == 0:

            messagebox.showwarning(
                "Attention",
                "Aucune photo analysée."
            )

            return

        path = filedialog.asksaveasfilename(
            title="Exporter les résultats",
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
                f"Fichier Excel créé avec succès :\n{path}"
            )

        except Exception as erreur:

            messagebox.showerror(
                "Erreur d'export",
                str(erreur)
            )

    # ==========================================
    # FERMETURE
    # ==========================================

    def fermer(self):

        self.thumbnail_cancel.set()

        self.generation += 1

        self.root.destroy()
