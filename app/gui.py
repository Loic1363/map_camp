import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import datetime
from tkintermapview import TkinterMapView
from app.data_manager import charger_lieux, sauvegarder_lieux, importer_lieux, exporter_lieux
from app.search import rechercher_lieu_api

class MapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carte France avec Recherche et Options")
        self.geometry("1000x700")

        self.lieux = charger_lieux()
        self.next_id = max(map(int, self.lieux.keys())) + 1 if self.lieux else 0
        self.fichier_sauvegarde = "lieux.json"

        self._build_gui()

    def _build_gui(self):
        self.search_frame = ttk.Frame(self)
        self.search_frame.place(x=10, y=10, width=420, height=40)

        self.menu_btn = ttk.Button(self.search_frame, text="≡", width=3)
        self.menu_btn.pack(side="left", padx=(5,5))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=30, fg='grey', font=('Segoe UI', 14))
        self.search_entry.pack(side="left", padx=(0,5), fill="x", expand=True)

        self.placeholder = "Rechercher dans Google Maps"
        self.search_entry.insert(0, self.placeholder)

        def on_focus_in(event):
            if self.search_entry.get() == self.placeholder:
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg='black')
        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, self.placeholder)
                self.search_entry.config(fg='grey')
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.search_entry.bind("<Return>", self.rechercher_lieu)

        self.search_icon = ttk.Button(self.search_frame, text="🔍", width=3, command=self.rechercher_lieu)
        self.search_icon.pack(side="left", padx=(0,3))
        self.send_btn = ttk.Button(self.search_frame, text="➤", width=3, command=self.rechercher_lieu)
        self.send_btn.pack(side="left", padx=(0,6))

        self.map_widget = TkinterMapView(self, width=700, height=700)
        self.map_widget.pack(side="left", fill="both", expand=True)
        self.map_widget.set_position(46.603354, 1.888334)
        self.map_widget.set_zoom(6)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.map_widget.max_zoom = 16
        self.map_widget.min_zoom = 4

        self.markers = {}

        self.options_frame = ttk.Notebook(self)
        self.options_frame.pack(side="right", fill="y", expand=False)
        self.tab_lieux = ttk.Frame(self.options_frame)
        self.options_frame.add(self.tab_lieux, text="Lieux enregistrés")

        self.lieux_listbox = tk.Listbox(self.tab_lieux, height=25)
        self.lieux_listbox.pack(fill="both", expand=True)
        self.lieux_listbox.bind("<<ListboxSelect>>", self.on_lieu_select)

        btn_modifier = ttk.Button(self.tab_lieux, text="Modifier nom", command=self.modifier_nom)
        btn_modifier.pack(fill="x")

        btn_supprimer = ttk.Button(self.tab_lieux, text="Supprimer lieu", command=self.supprimer_lieu)
        btn_supprimer.pack(fill="x")

        self.tab_ajout = ttk.Frame(self.options_frame)
        self.options_frame.add(self.tab_ajout, text="Ajout de lieu")

        self.ajout_activé = tk.BooleanVar(value=False)
        check_ajout = ttk.Checkbutton(self.tab_ajout, text="Activer ajout par clic sur la carte", variable=self.ajout_activé)
        check_ajout.pack()

        self.map_widget.add_left_click_map_command(self.clic_carte)

        btn_export = ttk.Button(self.tab_lieux, text="Exporter lieux...", command=self.exporter_lieux)
        btn_export.pack(fill="x", pady=(5,0))

        btn_import = ttk.Button(self.tab_lieux, text="Importer lieux...", command=self.importer_lieux)
        btn_import.pack(fill="x")

        self.maj_liste()
        self.afficher_markers()

    def rechercher_lieu(self, event=None):
        lieu = self.search_entry.get().strip()
        if not lieu or lieu == self.placeholder:
            messagebox.showwarning("Erreur", "Entrez un lieu à rechercher.")
            return
        coords = rechercher_lieu_api(lieu)
        if coords:
            lat, lon = coords
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_zoom(15)
        else:
            messagebox.showinfo("Aucun résultat", "Aucun lieu trouvé.")

    def maj_liste(self):
        self.lieux_listbox.delete(0, tk.END)
        for id_, info in self.lieux.items():
            self.lieux_listbox.insert(tk.END, f"{info['nom']} ({info['lat']:.4f}, {info['lon']:.4f})")

    def afficher_markers(self):
        for marker in self.markers.values():
            marker.delete()
        self.markers.clear()
        for id_, info in self.lieux.items():
            text = f"{info['nom']}\nDate: {info.get('date','')}\nRemarque: {info.get('remarque','')}"
            m = self.map_widget.set_marker(info['lat'], info['lon'], text=text)
            self.markers[id_] = m

    def on_lieu_select(self, event):
        selection = self.lieux_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        id_ = list(self.lieux.keys())[index]
        info = self.lieux[id_]
        self.map_widget.set_position(info['lat'], info['lon'])
        self.map_widget.set_zoom(15)

    def modifier_nom(self):
        selection = self.lieux_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un lieu dans la liste")
            return
        index = selection[0]
        id_ = list(self.lieux.keys())[index]
        info = self.lieux[id_]

        nouveau_nom = simpledialog.askstring("Modifier nom", "Nouveau nom :", initialvalue=info['nom'])
        if nouveau_nom:
            self.lieux[id_]['nom'] = nouveau_nom
            self.maj_liste()
            self.afficher_markers()
            sauvegarder_lieux(self.lieux)

    def supprimer_lieu(self):
        selection = self.lieux_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un lieu dans la liste")
            return
        index = selection[0]
        id_ = list(self.lieux.keys())[index]
        if messagebox.askyesno("Confirmation", f"Supprimer le lieu {self.lieux[id_]['nom']} ?"):
            del self.lieux[id_]
            self.maj_liste()
            self.afficher_markers()
            sauvegarder_lieux(self.lieux)

    def clic_carte(self, coordinates_tuple):
        if not self.ajout_activé.get():
            return
        lat, lon = coordinates_tuple
        nom = simpledialog.askstring("Nom du lieu", "Nom du lieu :", initialvalue="Nouveau lieu")
        if not nom:
            return
        date = simpledialog.askstring("Date", "Date (ex: 2025-11-06) :", initialvalue=datetime.now().strftime("%Y-%m-%d"))
        remarque = simpledialog.askstring("Remarque", "Remarque :", initialvalue="")

        self.lieux[str(self.next_id)] = {
            "lat": lat,
            "lon": lon,
            "nom": nom,
            "date": date,
            "remarque": remarque
        }
        self.next_id += 1
        self.maj_liste()
        self.afficher_markers()
        sauvegarder_lieux(self.lieux)

    def exporter_lieux(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("Fichiers JSON", "*.json")],
                                            title="Exporter les lieux")
        if not path:
            return
        try:
            exporter_lieux(self.lieux, path)
            messagebox.showinfo("Export réussi", f"Les lieux ont été exportés vers:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur export", f"Impossible d'exporter:\n{e}")

    def importer_lieux(self):
        path = filedialog.askopenfilename(defaultextension=".json",
                                          filetypes=[("Fichiers JSON", "*.json")],
                                          title="Importer les lieux")
        if not path:
            return
        try:
            new_lieux = importer_lieux(path)
            ids = set(self.lieux.keys())
            for key, val in new_lieux.items():
                if key in ids:
                    key = str(self.next_id)
                    self.next_id += 1
                self.lieux[key] = val
            self.maj_liste()
            self.afficher_markers()
            sauvegarder_lieux(self.lieux)
            messagebox.showinfo("Import réussi", f"Les lieux ont été importés depuis:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur import", f"Impossible d'importer:\n{e}")
