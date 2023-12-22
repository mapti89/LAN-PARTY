import xml.etree.ElementTree as ET
import requests
import time

def envoyer_requete(jeu, fichier):
    url_backend = 'http://torrent:5001/create_torrent'
    data = {'value': jeu, 'file_name': fichier}
    response = requests.post(url_backend, data=data)
    return response

def traiter_fichier_xml(chemin_fichier):
    # Charger le fichier XML
    tree = ET.parse(chemin_fichier)
    root = tree.getroot()

    # Parcourir chaque jeu dans le fichier XML
    for jeu_element in root.findall('jeu'):
        titre = jeu_element.find('titre').text
        fichier = jeu_element.find('fichier').text

        # Envoyer la requête pour chaque jeu
        response = envoyer_requete(titre, fichier)
        print(f"Requête envoyée pour {titre}: Réponse {response.status_code}")

# Chemin vers le fichier XML
chemin_fichier_xml = '/usr/src/app/mount/jeux.xml'
time.sleep(5) #dirty I know...
traiter_fichier_xml(chemin_fichier_xml)

