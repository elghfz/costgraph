import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from algos import detect_cycle, dijkstra, reconstruct_path, create_graph, calculate_cost_strategies

# --- Fonctions de navigation ---

# configuration du scroll pour les widgets
def gestionnaire_scroll(widget, command):
    widget.bind("<MouseWheel>", command, add='+')
    widget.bind("<Button-4>", command, add='+')
    widget.bind("<Button-5>", command, add='+')
    for child in widget.winfo_children():
        gestionnaire_scroll(child, command)

#création des frames scrollables
def create_scrollable_frame(parent):
    container = ttk.Frame(parent)
    canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    container.pack(fill=tk.BOTH, expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    def _scroll_canvas(event):
        scroll_amount = 0
        if event.num == 5 or event.delta < 0:
            scroll_amount = 1
        elif event.num == 4 or event.delta > 0:
            scroll_amount = -1
        canvas.yview_scroll(scroll_amount, "units")

    for widget in [canvas, scrollable_frame]:
         widget.bind("<MouseWheel>", _scroll_canvas, add='+')
         widget.bind("<Button-4>", _scroll_canvas, add='+')
         widget.bind("<Button-5>", _scroll_canvas, add='+')

    scrollable_frame._scroll_command = _scroll_canvas

    return scrollable_frame, canvas

# --- Classe principale ---

class CostGraph:
    #initialisation de la fenetre principale
    def __init__(self, root):
        self.root = root
        self.root.title("CostGraph - Optimisation des Coûts d'Approvisionnement")
        self.root.geometry("950x750")
        self.root.minsize(800, 600)

        self.installations = []
        self.frais_approvisionnement = tk.DoubleVar(value=2000)
        self.cout_stockage = tk.DoubleVar(value=2)
        self.nb_mois = tk.IntVar(value=6)

        style = ttk.Style()
        self.default_bg = style.lookup('TFrame', 'background')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.create_tabs()
        self.afficher_etape1()

    # les onglets
    def create_tabs(self):
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Configuration")

        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="Résultats")
        self.scrollable_results_frame, self.results_canvas = create_scrollable_frame(self.tab_results)

        self.frame_step1_content = None
        self.frame_step2_content = None

    # raccourcis pour vider les frames
    def vider_config_tab(self):
        for widget in self.tab_config.winfo_children():
            widget.destroy()
        self.frame_step1_content = None
        self.frame_step2_content = None

    def vider_resultats_tab(self):
        if hasattr(self, 'scrollable_results_frame') and self.scrollable_results_frame:
             for widget in self.scrollable_results_frame.winfo_children():
                 widget.destroy()

    # --- elements des etapes 1 et 2 (titre, boutons, input fields de texte...) ---
    def setup_etape(self, title, subtitle, widgets_callback):
        self.vider_config_tab()
        frame_content = ttk.Frame(self.tab_config)
        frame_content.pack(expand=True)

        center_wrapper = ttk.Frame(frame_content)
        center_wrapper.pack(expand=True)

        ttk.Label(center_wrapper, text="CostGraph", font=("Helvetica", 16, "bold")).pack(pady=(0, 5))
        ttk.Label(center_wrapper, text=subtitle, font=("Helvetica", 10)).pack(pady=(0, 15))

        title_frame = ttk.Frame(center_wrapper)
        title_frame.pack(pady=10)
        ttk.Label(title_frame, text=title, font=("Helvetica", 12, "bold")).pack()

        widgets_callback(center_wrapper)

    def afficher_etape1(self):
        def widgets(center_wrapper):
            params_frame = ttk.Frame(center_wrapper)
            params_frame.pack(pady=20)

            ttk.Label(params_frame, text="Nombre de mois:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
            nb_mois_spinbox = ttk.Spinbox(params_frame, from_=1, to=120, increment=1, textvariable=self.nb_mois, width=8)
            nb_mois_spinbox.grid(row=0, column=1, padx=5, pady=10)

            ttk.Label(params_frame, text="Frais fixes d'approvisionnement (€):").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
            ttk.Entry(params_frame, textvariable=self.frais_approvisionnement, width=10).grid(row=1, column=1, padx=5, pady=10)

            ttk.Label(params_frame, text="Coût de stockage par unité par mois (€):").grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
            cout_stockage_spinbox = ttk.Spinbox(params_frame, from_=0.0, to=1000.0, increment=1.0, textvariable=self.cout_stockage, width=8, format="%.2f")
            cout_stockage_spinbox.grid(row=2, column=1, padx=5, pady=10)

            button_frame = ttk.Frame(center_wrapper)
            button_frame.pack(pady=20)
            ttk.Button(button_frame, text="Suivant", command=self.afficher_etape2).pack()

        self.setup_etape(
            title="Étape 1: Paramètres généraux",
            subtitle="Optimisation des Coûts d'Approvisionnement",
            widgets_callback=widgets
        )

    def afficher_etape2(self):
        def widgets(center_wrapper):
            installations_outer_frame = ttk.Frame(center_wrapper)
            installations_outer_frame.pack(pady=10)
            installations_frame = ttk.Frame(installations_outer_frame)
            installations_frame.pack()

            self.installation_entries = []

            nb_mois = self.nb_mois.get()
            if not isinstance(nb_mois, int) or nb_mois <= 0:
                messagebox.showerror("Erreur", "Le nombre de mois doit être un entier positif.")
                self.nb_mois.set(6)
                nb_mois = 6

            if nb_mois > 48:
                messagebox.showwarning("Attention", f"Nombre de mois ({nb_mois}) élevé. L'interface et l'analyse peuvent être longues.")

            # Valeurs par défaut
            default_values = [200, 200, 300, 700, 1000, 200] * ((nb_mois // 6) + 1)

            cols = 3
            for i in range(nb_mois):
                row = i // cols
                col = i % cols
                frame = ttk.Frame(installations_frame)
                frame.grid(row=row, column=col, padx=15, pady=10, sticky=tk.W)
                ttk.Label(frame, text=f"Mois {i+1}:").pack(side=tk.LEFT, padx=(0, 5))
                entry = ttk.Entry(frame, width=8)
                entry.pack(side=tk.LEFT)
                entry.insert(0, str(default_values[i] if i < len(default_values) else 200))
                self.installation_entries.append(entry)

            button_frame = ttk.Frame(center_wrapper)
            button_frame.pack(pady=20)
            center_buttons_subframe = ttk.Frame(button_frame)
            center_buttons_subframe.pack(anchor="center")
            ttk.Button(center_buttons_subframe, text="Retour", command=self.afficher_etape1).pack(side=tk.LEFT, padx=10)
            ttk.Button(center_buttons_subframe, text="Lancer l'analyse", command=self.lancer_analyse).pack(side=tk.RIGHT, padx=10)

        self.setup_etape(
            title="Étape 2: Besoins mensuels d'installations",
            subtitle="Optimisation des Coûts d'Approvisionnement",
            widgets_callback=widgets
        )

    def get_installations(self):
        installations = []
        for i, entry in enumerate(self.installation_entries):
            value_str = entry.get()
            value = int(value_str)
            if value < 0:
                entry.config(foreground="red")
                messagebox.showerror("Erreur de saisie", f"La valeur pour le Mois {i+1} doit être positive ou nulle.")
                entry.focus_set()
                return None
            installations.append(value)
            entry.config(foreground="")
        self.installations = installations
        return self.installations

    # --- l'analyse est lancée ici après verif des inputs ---
    def lancer_analyse(self):
        if self.get_installations() is None:
             self.notebook.select(0)
             return

        frais_approvisionnement = self.frais_approvisionnement.get()
        cout_stockage = self.cout_stockage.get()
        if not isinstance(frais_approvisionnement, (int, float)) or frais_approvisionnement < 0:
             messagebox.showerror("Erreur", "Les frais d'approvisionnement doivent être un nombre positif ou nul.")
             self.notebook.select(0)
             self.afficher_etape1()
             return
        if not isinstance(cout_stockage, (int, float)) or cout_stockage < 0:
             messagebox.showerror("Erreur", "Le coût de stockage doit être un nombre positif ou nul.")
             self.notebook.select(0)
             self.afficher_etape1()
             return
        
        # logs pour le debug
        print("Analyse en cours...")
        print(f"Installations: {self.installations}")
        print(f"Frais Appro: {frais_approvisionnement}, Coût Stockage: {cout_stockage}")

        # utilisation des fonctions d'algo.py
        G, n_months = create_graph(self.installations, frais_approvisionnement, cout_stockage)
        
        if detect_cycle(G):
            messagebox.showerror("Erreur d'algorithme", "Le graphe généré contient des cycles.")
            return

        distances, predecessors = dijkstra(G, 0, n_months)
        
        if n_months not in distances or distances[n_months] == float('inf'):
            messagebox.showerror("Erreur d'algorithme", "Aucun chemin valide trouvé du début à la fin (coût infini).")
            return

        path = reconstruct_path(predecessors, 0, n_months)
        cout_optimal = distances[n_months]
        print(f"Chemin optimal trouvé: {path} Coût : {cout_optimal:.2f}")

        autres_couts = calculate_cost_strategies(self.installations, frais_approvisionnement, cout_stockage)
        print(f"Comparison costs: {autres_couts}")

        self.afficher_resultats(G, path, cout_optimal, autres_couts, frais_approvisionnement, cout_stockage, predecessors, n_months)
        self.notebook.select(1)

    # affichage des résultats
    def afficher_resultats(self, G, path, cout_optimal, autres_couts, frais_approvisionnement, cout_stockage, predecessors, n_months):
        self.vider_resultats_tab()
        main_frame = ttk.Frame(self.scrollable_results_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Résultats de l'analyse", font=("Helvetica", 12, "bold")).pack(anchor="center", pady=(5, 15))

        text_results_container = ttk.Frame(main_frame)
        text_results_container.pack(fill=tk.X, expand=False, pady=0, padx=0)

        text_optimal = tk.Text(text_results_container, wrap=tk.WORD, height=22,
                               font=("Consolas", 9), relief=tk.FLAT, borderwidth=0,
                               highlightthickness=0, bg=self.default_bg)
        text_optimal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 2), pady=5)

        text_comparison = tk.Text(text_results_container, wrap=tk.WORD, height=22,
                                  font=("Consolas", 9), relief=tk.FLAT, borderwidth=0,
                                  highlightthickness=0, bg=self.default_bg)
        text_comparison.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 5), pady=5)

        for txt_widget in [text_optimal, text_comparison]:
            txt_widget.tag_configure("title", font=("Helvetica", 10, "bold"), spacing1=5, spacing3=5, foreground="#003366")
            txt_widget.tag_configure("normal", font=("Consolas", 9), lmargin1=10, lmargin2=10)
            txt_widget.tag_configure("cost", font=("Consolas", 9, "bold"), foreground="green")
            txt_widget.tag_configure("negcost", font=("Consolas", 9, "bold"), foreground="red")
            txt_widget.tag_configure("path", font=("Consolas", 9, "italic"), lmargin1=20, lmargin2=20)
            txt_widget.tag_configure("warning", font=("Consolas", 9), foreground="orange")
            txt_widget.tag_configure("comp_label", font=("Consolas", 9), lmargin1=10, lmargin2=10)
            txt_widget.tag_configure("comp_cost", font=("Consolas", 9, "bold"), lmargin1=10, lmargin2=10)

        text_optimal.insert(tk.END, "1. Stratégie Optimale :\n", "title")
        text_optimal.insert(tk.END, "   Coût total minimum trouvé : ", "normal")
        text_optimal.insert(tk.END, f"{cout_optimal:,.2f} €\n", "cost")
        text_optimal.insert(tk.END, "   Politique d'approvisionnement :\n", "normal")


        total_fixed_cost_actual = 0
        if len(path) > 1: 
            total_fixed_cost_actual = (len(path) - 1) * frais_approvisionnement
        total_stock_cost_actual = cout_optimal - total_fixed_cost_actual

        for i in range(len(path) - 1):
            mois_debut_idx = path[i]
            mois_fin_idx = path[i+1]
            month_label_start = mois_debut_idx + 1
            month_label_end = mois_fin_idx
            quantite = sum(self.installations[mois_debut_idx:mois_fin_idx])

            batch_cost = G[mois_debut_idx][mois_fin_idx]['weight']

            text_optimal.insert(tk.END, f"   - Début Mois {month_label_start}: Commander ", "normal")
            text_optimal.insert(tk.END, f"{quantite}", "cost")
            text_optimal.insert(tk.END, f" unités (pour Mois {month_label_start} à {month_label_end}).\n", "normal")
            text_optimal.insert(tk.END, f"     Coût (Fixe + Stockage): {batch_cost:,.2f} €\n", "path")


        text_optimal.insert(tk.END, f"\n   Répartition Coût Optimal: Fixe {total_fixed_cost_actual:,.2f} € + Stockage {total_stock_cost_actual:,.2f} €\n", "normal")


        text_comparison.insert(tk.END, "2. Comparaison avec Stratégies Simples:\n", "title")
        cost_achats = autres_couts['directeur_achats']
        cost_financier = autres_couts['directeur_financier']
        text_comparison.insert(tk.END, "   Stratégie 'Tout au début' : ", "comp_label")
        text_comparison.insert(tk.END, f"{cost_achats:,.2f} €\n", "comp_cost" if cost_achats >=0 else "negcost")
        text_comparison.insert(tk.END, "   Stratégie 'Mois par mois' : ", "comp_label")
        text_comparison.insert(tk.END, f"{cost_financier:,.2f} €\n", "comp_cost" if cost_financier >=0 else "negcost")

        economie_vs_achats = cost_achats - cout_optimal
        economie_vs_financier = cost_financier - cout_optimal
        percent_vs_achats = (economie_vs_achats / cost_achats * 100) if cost_achats > 0 else 0
        percent_vs_financier = (economie_vs_financier / cost_financier * 100) if cost_financier > 0 else 0

        text_comparison.insert(tk.END, f"\n3. Économies Potentielles vs Optimale:\n", "title")
        text_comparison.insert(tk.END, "   'Tout au début': ", "comp_label")
        text_comparison.insert(tk.END, f"{economie_vs_achats:,.2f} € ({percent_vs_achats:.1f}%)\n", "cost" if economie_vs_achats >=0 else "negcost")
        text_comparison.insert(tk.END, "   'Mois par mois': ", "comp_label")
        text_comparison.insert(tk.END, f"{economie_vs_financier:,.2f} € ({percent_vs_financier:.1f}%)\n", "cost" if economie_vs_financier >=0 else "negcost")

        text_optimal.configure(state='disabled')
        text_comparison.configure(state='disabled')

        self.afficher_graphiques(main_frame, n_months, predecessors, frais_approvisionnement, cout_stockage)

        ttk.Button(main_frame, text="Retour à la configuration",
                  command=lambda: self.notebook.select(0)).pack(pady=20)

        if hasattr(self.scrollable_results_frame, '_scroll_command'):
            gestionnaire_scroll(main_frame, self.scrollable_results_frame._scroll_command)

# --- Visualisation des résultats de deux façons : évoltion des coûts par mois par strat et achats optimaux à faire ---
    def afficher_graphiques(self, parent, n_months, predecessors, frais_approvisionnement, cout_stockage):
        chart_container_frame = ttk.LabelFrame(parent, text="Graphiques")
        chart_container_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        fig = Figure(figsize=(8, 9))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        mois = list(range(n_months + 1))

        # --- calculs des couts pour les trois stratégies ---

        # en une fois
        cout_une_fois = [0.0] * (n_months + 1)
        cout_total = frais_approvisionnement + sum(self.installations)
        cout_une_fois[0] = 0.0
        if n_months > 0 :
             stock = sum(self.installations)
             for i in range(n_months):
                 stock -= self.installations[i]
                 cout_stockage_mois = stock * cout_stockage
                 cout_total += cout_stockage_mois
                 cout_une_fois[i+1] = cout_total

        # mensuel
        cout_mensuel = [0.0] * (n_months + 1)
        stock = 0.0
        total_cost = 0.0
        cout_mensuel[0] = 0.0

        for i in range(n_months):
            total_cost += frais_approvisionnement + self.installations[i]
            stock += self.installations[i]
            stock -= self.installations[i]
            cout_stockage_mois = stock * cout_stockage
            total_cost += cout_stockage_mois
            cout_mensuel[i+1] = total_cost

        # optimal obtenu par l'algo de Dijkstra
        chemin_optimal = reconstruct_path(predecessors, 0, n_months)
        cout_optimal = [0.0] * (n_months + 1)
        achats_optimaux = [0] * n_months
        cout_optimal[0] = 0.0

        cout_actuel = 0.0
        stock = 0.0
        id_prochain_appro = 1

        for i in range(n_months):
            # vérifie si le mois actuel (i) correspond à un point d'approvisionnement dans le chemin optimal
            if id_prochain_appro < len(chemin_optimal) and i == chemin_optimal[id_prochain_appro-1]:
                # si un approvisionnement est necessaire, on détermine la période couverte par cet approvisionnement
                mois_debut = chemin_optimal[id_prochain_appro-1]
                mois_fin = chemin_optimal[id_prochain_appro]
                achats_optimaux[i] = sum(self.installations[mois_debut:mois_fin])
                # la quantite qu'il faut acheter est la somme des besoins entre ces deux mois
                cout_actuel += frais_approvisionnement + achats_optimaux[i]
                stock += achats_optimaux[i]
                id_prochain_appro += 1

            stock -= self.installations[i]

            cout_stockage_mois = stock * cout_stockage
            cout_actuel += cout_stockage_mois
            # Le cout total est cumulé jusqu'à la fin du mois actuel est enregistré ici
            cout_optimal[i+1] = cout_actuel

        # --- config des graphiques --

        ax1.plot(mois, cout_mensuel, label="Achats mensuels", color='#c9c1bc', marker='o', linestyle=':')
        ax1.plot(mois, cout_une_fois, label="Achat unique (début)", color='#c9c1bc', marker='x', linestyle='--')
        ax1.plot(mois, cout_optimal, label="Stratégie Optimale", color='#ef7645', marker='s', linewidth=2)

        ax1.set_xlabel('Fin du Mois (Noeud)')
        ax1.set_ylabel('Coût total cumulé (€)')
        ax1.set_title("Évolution des coûts cumulés par stratégie")
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.set_xticks(mois)
        ax1.set_xticklabels([str(m) for m in mois])

        mois_labels_bar = [f"Mois {i+1}" for i in range(n_months)]
        bars = ax2.bar(mois_labels_bar, achats_optimaux, color='#ef7645', label='Quantité achetée')
        ax2.set_xlabel('Mois de commande')
        ax2.set_ylabel('Unités commandées')
        ax2.set_title('Stratégie Optimale: Commandes par mois')
        ax2.grid(True, axis='y', linestyle='--', alpha=0.6)

        ax2.bar_label(bars, fmt='%g', padding=3, fontsize=9,
                      labels=[f'{v}' if v > 0 else '' for v in achats_optimaux])

        ax2b = ax2.twinx()
        ax2b.plot(mois_labels_bar, self.installations, color='grey', linestyle=':', marker='.', label='Besoins (Installations)')
        ax2b.set_ylabel('Unités nécessaires', color='grey')
        ax2b.tick_params(axis='y', labelcolor='grey')
        lines, labels = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2b.legend(lines + lines2, labels + labels2, loc='upper right')

        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=chart_container_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        canvas.draw()


def main():
    root = ThemedTk(theme="radiance")
    app = CostGraph(root)
    root.mainloop()

if __name__ == "__main__":
    main()