from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
from xml.etree import ElementTree as ET
import os
import requests
import shutil

app = Flask(__name__)
CORS(app)

# Paths to folders
data_folder = 'data/'
img_folder = 'img/'
xml_file = 'xml/jeux.xml'
torrent_folder = 'torrent'

# URL of the servers
url_web_server = 'http://127.0.0.1/'

# Home page
@app.route('/')
def index():
    return Response("Welcome to LAN PARTY", status=200)

# Function to check if the game title is unique
def titre_unique(titre):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    titres = root.findall("./jeu/titre")
    for titre_elem in titres:
        if titre_elem.text == titre:
            return False
    return True

# Adding a game with creation of a directory for each game
@app.route('/ajouter_jeu', methods=['POST'])
def ajouter_jeu():
    if request.method == 'POST':
        titre = request.form['titre']
        fichier = request.files['fichier']
        descriptif = request.form['descriptif']
        image = request.files['image']

        if not titre_unique(titre):
            return Response("The game title already exists. Please choose a unique title.", status=400)

        # Creating the directory for the game (if it does not already exist)
        chemin_repertoire_jeu = os.path.join(data_folder, titre)
        if not os.path.exists(chemin_repertoire_jeu):
            os.makedirs(chemin_repertoire_jeu)

        # Saving the game file in the corresponding directory
        chemin_fichier_jeu = os.path.join(chemin_repertoire_jeu, fichier.filename)
        fichier.save(chemin_fichier_jeu)

        # Saving the game image in the corresponding directory
        chemin_image_jeu = os.path.join(chemin_repertoire_jeu, image.filename)
        image.save(chemin_image_jeu)
        
        # Adding information in the XML file
        ajouter_jeu_xml(titre, fichier.filename, descriptif, image.filename, "in progress")

        # POST request to the torrent creation service
        url_backend = 'http://torrent:5001/create_torrent'
        data = {'value': (titre), 'file_name': (fichier.filename)}
        response = requests.post(url_backend, data=data)
    
        if response.status_code != 200:
            return Response("Error creating the torrent: " + response.text, status=400)

        return Response("Game successfully added!", status=200)
    
# Function to add a game in the XML file
def ajouter_jeu_xml(titre, fichier, descriptif, image, torrent_status):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    jeu = ET.Element("jeu")
    titre_elem = ET.SubElement(jeu, "titre")
    titre_elem.text = titre
    fichier_elem = ET.SubElement(jeu, "fichier")
    fichier_elem.text = fichier
    descriptif_elem = ET.SubElement(jeu, "descriptif")
    descriptif_elem.text = descriptif
    image_elem = ET.SubElement(jeu, "image")
    image_elem.text = image
    torrent_elem = ET.SubElement(jeu, "torrent")
    torrent_elem.text = torrent_status

    root.append(jeu)
    tree.write(xml_file)

# Function to list games (title, file URL, image URL, description)
def lister_jeux():
    tree = ET.parse(xml_file)
    root = tree.getroot()
    jeux = []

    for jeu in root.findall('jeu'):
        titre = jeu.find('titre').text
        fichier = jeu.find('fichier').text
        image = jeu.find('image').text
        description = jeu.find('descriptif').text

        # Create URLs for the file and image using the game directory
        chemin_repertoire_jeu = os.path.join(data_folder, titre)
        url_fichier = url_web_server + chemin_repertoire_jeu + '/' + fichier if os.path.exists(os.path.join(chemin_repertoire_jeu, fichier)) else None
        url_image = url_web_server + chemin_repertoire_jeu + '/' + image if os.path.exists(os.path.join(chemin_repertoire_jeu, image)) else None

        # Add game details to the list
        jeux.append({
            'titre': titre,
            'url_fichier': url_fichier,
            'url_image': url_image,
            'description': description
        })

    return jeux

# Function to display games
@app.route('/liste_jeux', methods=['GET'])
def afficher_jeux():
    jeux = lister_jeux()

    # Créer une liste de dictionnaires pour chaque jeu
    jeux_json = []
    for jeu in jeux:
        jeux_json.append({
            'titre': jeu['titre'],
            'url_fichier': jeu['url_fichier'],
            'url_image': jeu['url_image'],
            'description': jeu['description']
        })

    # Utiliser jsonify pour convertir la liste en JSON et la retourner
    return jsonify(jeux_json)

# Function to delete a game from the XML file (and its directory)
@app.route('/effacer_jeu/<titre>', methods=['DELETE'])
def effacer_jeu(titre):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    jeu_trouve = False

    for jeu in root.findall('jeu'):
        if jeu.find('titre').text == titre:
            jeu_trouve = True
            torrent_name = jeu.find('torrent').text
            root.remove(jeu)
            tree.write(xml_file)

            # Delete the game directory (including the file and image)
            chemin_repertoire_jeu = os.path.join(data_folder, titre)
            if os.path.exists(chemin_repertoire_jeu):
                import shutil
                shutil.rmtree(chemin_repertoire_jeu)
            
            # Delete torrent file if its name is not "in progress"
            if torrent_name != "in progress":
                chemin_fichier_torrent = os.path.join(torrent_folder, torrent_name)
                if os.path.isfile(chemin_fichier_torrent):
                    os.remove(chemin_fichier_torrent)

            return Response(f"Game '{titre}' successfully deleted!", status=200)

    if not jeu_trouve:
        return Response(f"The game with the title '{titre}' does not exist.", status=400)

@app.route('/update_game_description', methods=['POST'])
def update_game_description():
    data = request.json
    game_title = data.get('title')
    new_description = data.get('description')

    if not game_title or not new_description:
        return jsonify({"error": "Missing title or description"}), 400

    if update_descriptif_in_xml(xml_file, game_title, new_description):
        return jsonify({"message": "Description updated successfully"}), 200
    else:
        return jsonify({"error": "Game not found"}), 404

    
def update_descriptif_in_xml(xml_file, game_title, new_description):
    # Load and parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the game with the specified title and update its description
    game_found = False
    for jeu in root.findall('jeu'):
        if jeu.find('titre').text == game_title:
            descriptif = jeu.find('descriptif')
            descriptif.text = new_description
            game_found = True
            break

    # Save the modifications in the XML file
    if game_found:
        tree.write(xml_file)
        return True
    else:
        return False  # Return False if the game was not found

@app.route('/update_game_image', methods=['POST'])
def update_game_image():
    game_title = request.form.get('title')
    image_file = request.files.get('image')

    if not game_title or not image_file:
        return Response("Missing title or image", status=400)

    if update_image_in_xml(xml_file, game_title, image_file.filename, image_file):
        return Response("Image updated successfully", status=200)
    else:
        return Response("Game not found", status=404)

def update_image_in_xml(xml_file, game_title, new_image_name, new_image_file):
    # Load and parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the game with the specified title and update its image
    for jeu in root.findall('jeu'):
        if jeu.find('titre').text == game_title:
            image_elem = jeu.find('image')
            old_image_path = os.path.join(f'data/{game_title}', image_elem.text)

            # Delete the old image if it exists
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)

            # Update the XML with the new image name
            image_elem.text = new_image_name

            # Save the new image in the 'img/' directory
            new_image_path = os.path.join(f'data/{game_title}', new_image_name)
            with open(new_image_path, 'wb') as image_file:
                shutil.copyfileobj(new_image_file.stream, image_file)

            # Save changes to the XML file
            tree.write(xml_file)
            return True
    return False

def update_title_and_rename_directory(xml_file, old_title, new_title):
    # Vérifie si le nouveau répertoire existe déjà
    new_directory_path = os.path.join('data/', new_title)
    if os.path.exists(new_directory_path):
        return False, "New directory name already exists."

    # Charger et parser le fichier XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Trouver le jeu et mettre à jour le titre
    for jeu in root.findall('jeu'):
        if jeu.find('titre').text == old_title:
            jeu.find('titre').text = new_title

            # Renommer le répertoire
            old_directory_path = os.path.join('data/', old_title)
            os.rename(old_directory_path, new_directory_path)

            # Sauvegarder les modifications dans le fichier XML
            tree.write(xml_file)
            return True, "Title updated and directory renamed successfully."

    return False, "Game not found."

@app.route('/update_game_title', methods=['POST'])
def update_game_title():
    data = request.json  # Récupérer les données JSON de la requête
    old_title = data.get('old_title')
    new_title = data.get('new_title')

    if not old_title or not new_title:
        return jsonify({"error": "Missing old or new title"}), 400

    success, message = update_title_and_rename_directory(xml_file, old_title, new_title)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
