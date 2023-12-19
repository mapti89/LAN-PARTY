from flask import Flask, request
import os
from torrentool.api import Torrent
from datetime import datetime
import xml.etree.ElementTree as ET

xml_file = 'xml/jeux.xml'
absolute_path = os.path.dirname(__file__)

app = Flask(__name__)

@app.route('/create_torrent', methods=['POST'])
def create_torrent_api():
    value = request.form.get('value')
    file_name = request.form.get('file_name')

    # Assume 'data' directory contains directories named by 'value'
    directory_path = f'data/{value}/'
    
    # Check if the directory exists
    if os.path.exists(directory_path):
        # Process the file located in the directory_path with the given file_name
        file_path = os.path.join(absolute_path, directory_path, file_name)
        if os.path.exists(file_path):
            # Create a torrent
            torrent_file_name = f'{file_name}.torrent'
            DL_path =  os.path.join(directory_path, file_name)
            torrent_path = f'{os.path.join("torrent/", file_name)}.torrent'
            torrent_url = f'http://127.0.0.1/{torrent_path}'
            torrent = Torrent.create_from(file_path)
            torrent.private = True
            torrent.webseeds = f'http://127.0.0.1:8080/{DL_path}'
            torrent.announce_urls = 'udp://127.0.0.1:6969'
            torrent.comment = "Torrent automatically created on " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            torrent.to_file(torrent_path)
            update_torrent_in_xml(value, torrent_file_name)
            return f'Torrent created and registered: {torrent_file_name}'
        else:
            return 'File not found', 404
    else:
        return 'Value directory not found', 404
    
def update_torrent_in_xml(game_title, new_torrent_file):
    # Load and parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the game with the specified title and update the torrent link
    for jeu in root.findall('jeu'):
        titre = jeu.find('titre').text
        if titre == game_title:
            torrent = jeu.find('torrent')
            torrent.text = new_torrent_file
            break

    # Save the modifications in the XML file
    tree.write(xml_file)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
