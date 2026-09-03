################################################################################
################################### Library ####################################
################################################################################


import time
import requests
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import math
import threading


import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import os




################################################################################
################################## Fonctions ###################################
################################################################################


class SatelliteInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Satellite Tracker")
        self.root.geometry("700x500")
        self.root.configure(bg="#1a1a2e")

        self.filepath_satellite = None
        self.filepath_api_key = None

        # Le fond d'origine n'est pas indispensable au fonctionnement et n'est
        # pas distribué tant que ses droits de réutilisation ne sont pas établis.
        if os.path.exists("background.jpg"):
            self.bg_image = Image.open("background.jpg")
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(relwidth=1, relheight=1, x=0, y=0)

        self.create_widgets()

    def create_widgets(self):
        font_style = ("Arial", 12, "bold")
        button_style = {"bg": "#16213e", "fg": "white", "font": ("Arial", 10, "bold"), "bd": 3}

        self.label_satellite = tk.Label(self.root, text="Fichier CSV des satellites :", fg="white", bg="#1a1a2e", font=font_style)
        self.label_satellite.pack(pady=10)
        self.btn_select_satellite = tk.Button(self.root, text="Sélectionner", command=self.load_satellite_file, **button_style)
        self.btn_select_satellite.pack()

        self.label_api_key = tk.Label(self.root, text="Fichier CSV des comptes API :", fg="white", bg="#1a1a2e", font=font_style)
        self.label_api_key.pack(pady=10)
        self.btn_select_api_key = tk.Button(self.root, text="Sélectionner", command=self.load_api_key_file, **button_style)
        self.btn_select_api_key.pack()

        self.btn_start = tk.Button(self.root, text="Commencer", command=threading.Thread(target=self.start_processing).start, **button_style)
        self.btn_start.pack(pady=20)

        self.progress_label = tk.Label(self.root, text="En attente...", fg="white", bg="#1a1a2e", font=font_style)
        self.progress_label.pack()

        self.results_text = tk.Text(self.root, width=60, height=10, bg="#0f3460", fg="white", font=("Arial", 10))
        self.results_text.pack(pady=10)

    def load_satellite_file(self):
        self.filepath_satellite = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.filepath_satellite:
            self.label_satellite.config(text=f"Fichier : {os.path.basename(self.filepath_satellite)}")

    def load_api_key_file(self):
        self.filepath_api_key = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.filepath_api_key:
            self.label_api_key.config(text=f"Fichier : {os.path.basename(self.filepath_api_key)}")

    def start_processing(self):
        if not self.filepath_satellite or not self.filepath_api_key:
            messagebox.showerror("Erreur", "Veuillez sélectionner les fichiers CSV.")
            return

        self.progress_label.config(text="Traitement en cours...")
        self.root.after(100, lambda: self.run_main())

    def run_main(self):
        try:
            main(self.filepath_satellite, self.filepath_api_key, self.display_results, self.update_progress)
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
            self.update_progress("Erreur pendant le traitement.")

    def update_progress(self, message):
        self.progress_label.config(text=message)

    def display_results(self, message):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, message)

def main(fichier, api_key, display_results, update_progress):
    def call_api(url):
        response = requests.get(url, timeout=25)
        return response.json()

    def affichage(resultats):
        resultats_plus_proche = (Karatsuba(get_position(resultats)))
        message = f'Les satellites "{resultats_plus_proche[1][0][0]}" et "{resultats_plus_proche[2][0][0]}" sont les plus proches, ils sont à une distance de {resultats_plus_proche[0]} km, et leurs coordonnées sont respectivement {resultats_plus_proche[1][1]} et {resultats_plus_proche[2][1]}'
        display_results(message)

    def lire_csv(fichier):
        liste_norad_id = []
        with open(fichier, mode='r', encoding='latin-1') as f:
            lecteur_csv = csv.reader(f, delimiter=';')
            entete = next(lecteur_csv)
            entete = [colonne.strip() for colonne in entete]
            index_norad = entete.index('NORAD Number')
            for ligne in lecteur_csv:
                if len(ligne) > index_norad:
                    norad_id = ligne[index_norad].strip()
                    liste_norad_id.append(norad_id)
        return liste_norad_id

    def get_api_key(fichier):
        liste = []
        with open(fichier, mode='r', encoding='latin-1') as f:
            lecteur_csv = csv.reader(f, delimiter=';')
            entete = next(lecteur_csv)
            entete = [colonne.strip() for colonne in entete]
            index_E = entete.index('api id')
            for ligne in lecteur_csv:
                liste.append(ligne[index_E].strip())
        return liste

    liste_norad_id = lire_csv(fichier)
    liste_api_key = get_api_key(api_key)
    nb_element = len(liste_norad_id)
    nb_compte = len(liste_api_key)

    comte_menthe_et_cristaux = 0
    comte_api = 0
    resultats = []

    update_progress(f"Traitement en cours : {comte_menthe_et_cristaux} / {nb_element} satellites récupérés.")

    while comte_menthe_et_cristaux < nb_element:


        information = call_api(f"https://api.n2yo.com/rest/v1/satellite/positions/40018/43.633119/1.394142/0/1/&apiKey={liste_api_key[comte_api]}")
        print(information,comte_menthe_et_cristaux)

        if "info" in information:
            transaction = information['info']['transactionscount']
            if comte_menthe_et_cristaux + (1000 - transaction) > nb_element:
                with ThreadPoolExecutor(max_workers=nb_element - comte_menthe_et_cristaux) as executor:
                    futures = {}
                    for i in range(comte_menthe_et_cristaux, nb_element):
                        futures[executor.submit(call_api, f"https://api.n2yo.com/rest/v1/satellite/positions/{liste_norad_id[i]}/43.633119/1.394142/0/1/&apiKey={liste_api_key[comte_api]}")] = f"https://api.n2yo.com/rest/v1/satellite/positions/{liste_norad_id[i]}/43.633119/1.394142/0/1/&apiKey={liste_api_key[comte_api]}"
                    resultats += [future.result() for future in futures]
            else:
                with ThreadPoolExecutor(max_workers=1000 - transaction) as executor:
                    futures = {}
                    for i in range(1000 - transaction):
                        futures[executor.submit(call_api, f"https://api.n2yo.com/rest/v1/satellite/positions/{liste_norad_id[i + comte_menthe_et_cristaux]}/43.633119/1.394142/0/1/&apiKey={liste_api_key[comte_api]}")] = f"https://api.n2yo.com/rest/v1/satellite/positions/{liste_norad_id[i + comte_menthe_et_cristaux]}/43.633119/1.394142/0/1/&apiKey={liste_api_key[comte_api]}"
                    resultats += [future.result() for future in futures]
            comte_menthe_et_cristaux += 1000 - transaction


        update_progress(f"Traitement en cours : {comte_menthe_et_cristaux} / {nb_element} satellite récupéré.")

        comte_api += 1
        if comte_api >= nb_compte:
            comte_api = 0
    update_progress(f"Récupération des satellites finis : {nb_element} / {nb_element} satellite récupéré.")

    affichage(resultats)

def get_position(information):
    positions_satellite = {}
    for element in information:
        if 'positions' in element:
            positions_satellite[(element['info']['satname'], element['info']['satid'])] = (element['positions'][0]['satlatitude'], element['positions'][0]['satlongitude'], element['positions'][0]['sataltitude'])


    return positions_satellite

def Karatsuba(E: dict) -> tuple:
    if len(E) <= 3:
        return points_proches(E)

    E_sorted = dict(sorted(E.items(), key=lambda item: item[1][0]))
    mediane = len(E_sorted) // 2

    x_0 = E_sorted[list(E_sorted.keys())[mediane]][0]

    E1 = {key: value for key, value in list(E_sorted.items())[:mediane]}
    E2 = {key: value for key, value in list(E_sorted.items())[mediane:]}

    d1 = Karatsuba(E1)
    d2 = Karatsuba(E2)

    delta = min(d1[0], d2[0])
    bande = {}

    for key, point in E_sorted.items():
        if x_0 - delta <= point[0] <= x_0 + delta:
            bande[key] = point

    distance_bande = proche_bande(bande)
    return min(d1, d2, distance_bande, key=lambda x: x[0])

def points_proches(E: dict) -> tuple:
    min_distance = float('inf')
    points_plus_proche = (None, None)
    clefs_points_proches = (None, None)
    keys = list(E.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1 = E[keys[i]]
            p2 = E[keys[j]]
            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

            if  dist < min_distance and not same_item(keys[i][0], keys[j][0]):
                min_distance = dist
                points_plus_proche = (p1, p2)
                clefs_points_proches = (keys[i], keys[j])

    return min_distance, (clefs_points_proches[0], points_plus_proche[0]), (clefs_points_proches[1], points_plus_proche[1])

def proche_bande(E: dict) -> tuple:
    distanceMinimum = float('inf'), (0, 0, 0), (0, 0, 0)
    clefs_points_proches = (None, None)
    points_plus_proche = (None, None)

    if len(E) < 2:
        return distanceMinimum

    keys = list(E.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1 = E[keys[i]]
            p2 = E[keys[j]]
            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

            if  dist < distanceMinimum[0] and not same_item(keys[i][0], keys[j][0]):
                distanceMinimum = dist, p1, p2
                clefs_points_proches = keys[i], keys[j]
                points_plus_proche = p1, p2

    return distanceMinimum[0], (clefs_points_proches[0], points_plus_proche[0]), (clefs_points_proches[1], points_plus_proche[1])

def same_item(satellite1, satellite2):


    if satellite1[:satellite1.find(' ')] in ['INTELSAT','MEV'] and satellite2[:satellite2.find('-')] in ['INTELSAT','MEV'] :
        return True

    elif satellite1[:satellite1.find('-')] in ['INTELSAT','MEV'] and satellite2[:satellite2.find(' ')] in ['INTELSAT','MEV']:
        return True

    if satellite1[:satellite1.find(' ')] in ['TANDEM','TERRA'] and satellite2[:satellite2.find(' ')] in ['TANDEM','TERRA'] :
        return True


    delimiteurs = [' ','-']
    for delimiteur in delimiteurs:
        if satellite1.find(delimiteur):
            if satellite1[:satellite1.find(delimiteur)] == satellite2[:satellite1.find(delimiteur)]:

                return True
    return False


################################################################################
################################### Programme ##################################
################################################################################

if __name__ == "__main__":
    root = tk.Tk()
    app = SatelliteInterface(root)
    root.mainloop()
