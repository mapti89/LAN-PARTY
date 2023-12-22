import os

def setup_directories_and_file():
    directories = ["/usr/src/app/mount/data", "/usr/src/app/mount/xml", "/usr/src/app/mount/torrent"]
    file_path = "/usr/src/app/mount/xml/jeux.xml"
    file_content = "<jeux>\n</jeux>"

    # Create directories if they don't exist
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Check and create the file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(file_content)

    return "Directories and file setup completed."

# Note: Run this function in your Python environment
setup_directories_and_file()
#url_web_server = os.environ.get('URL_WEB_SERVER')
#file_path = '/usr/src/app/webadmin/script.js'
#search_string = "const BASE_URL ="
#replace_string = "const BASE_URL = '" + url_web_server + "':5000"
## Lire le contenu du fichier
#with open(file_path, 'r') as file:
#    file_contents = file.read()
#
## Remplacer la chaîne
#file_contents = file_contents.replace(search_string, replace_string)
#
## Réécrire le fichier avec le contenu modifié
#with open(file_path, 'w') as file:
#    file.write(file_contents)