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
