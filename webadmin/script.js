const BASE_URL = 'http://127.0.0.1:5000';

function loadGames() {
    console.log("Chargement des jeux...");
    fetch(`${BASE_URL}/liste_jeux`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Réponse réseau non OK');
            }
            return response.json();
        })
        .then(games => {
            console.log("Jeux chargés :", games);
            const gameList = document.getElementById('gameList');
            gameList.innerHTML = ''; // Nettoie la liste existante

            games.forEach(game => {
                const gameDiv = document.createElement('div');
                gameDiv.className = 'game';
                gameDiv.innerHTML = `
                    <h3>${game.titre}</h3>
                    <p>${game.description}</p>
                    <img src="${game.url_image}" alt="Image de ${game.titre}">
                    <a href="${game.url_fichier}" target="_blank">Télécharger le jeu</a>
                    <button onclick="editGameTitle('${game.titre}')">Éditer Titre</button>
                    <button onclick="editGame('${game.titre}', 'description')">Éditer Descriptif</button>
                    <button onclick="editGameImage('${game.titre}')">Éditer Image</button>
                    <button onclick="deleteGame('${game.titre}')">Supprimer</button>
                `;

                gameList.appendChild(gameDiv);
            });
            
        })
        .catch(error => console.error('Erreur lors du chargement des jeux:', error));
}

function editGameImage(gameTitle) {
    document.getElementById('editImageGameTitle').value = gameTitle;
    document.getElementById('editImageModal').style.display = 'block';
}

function closeImageModal() {
    document.getElementById('editImageModal').style.display = 'none';
}

function deleteGame(gameTitle) {
    fetch(`${BASE_URL}/effacer_jeu/${gameTitle}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                loadGames(); // Recharger la liste des jeux après la suppression
            } else {
                alert('Erreur lors de la suppression du jeu');
            }
        });
}
function editGame(gameTitle, attribute) {
    if (attribute === 'description') {
        document.getElementById('editGameTitle').value = gameTitle;
        // Ici, vous pouvez aussi remplir le textarea avec la description actuelle si nécessaire
        document.getElementById('editModal').style.display = 'block';
    }
    // Vous pouvez étendre cette fonction pour d'autres attributs si nécessaire
}
function editGameTitle(gameId) {
    // Logique pour ouvrir le modal et remplir les champs
    document.getElementById('editTitleGameId').value = gameId;
    document.getElementById('editTitleModal').style.display = 'block';
}
function closeModal() {
    document.getElementById('editModal').style.display = 'none';
}
function closeTitleModal() {
    document.getElementById('editTitleModal').style.display = 'none';
}
function showAddGameModal() {
    document.getElementById('addGameModal').style.display = 'block';
}

function closeAddGameModal() {
    document.getElementById('addGameModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    loadGames();

    // Gestionnaire pour le formulaire d'édition
    document.getElementById('editForm').addEventListener('submit', function(e) {
        e.preventDefault(); // Empêche le rechargement de la page

        const gameTitle = document.getElementById('editGameTitle').value;
        const newDescription = document.getElementById('editDescription').value;

        updateGameDescription(gameTitle, newDescription);
    });
    document.getElementById('editTitleForm').addEventListener('submit', function(e) {
        e.preventDefault();
    
        const gameId = document.getElementById('editTitleGameId').value;
        //const gameTitle = document.getElementById('editGameTitle').value;
        const newTitle = document.getElementById('newGameTitle').value;
    
        updateGameTitle(gameId, newTitle);
    });    
    document.getElementById('editImageForm').addEventListener('submit', function(e) {
        e.preventDefault();
    
        const gameTitle = document.getElementById('editImageGameTitle').value;
        const imageFile = document.getElementById('newGameImage').files[0];
    
        updateGameImage(gameTitle, imageFile);
    });
    document.getElementById('addGameForm').addEventListener('submit', function(e) {
        e.preventDefault();
    
        const formData = new FormData();
        formData.append('titre', document.getElementById('gameTitle').value);
        formData.append('descriptif', document.getElementById('gameDescription').value);
        formData.append('image', document.getElementById('gameImage').files[0]);
        formData.append('fichier', document.getElementById('gameFile').files[0]);
    
        addGame(formData);
    });
});

function updateGameImage(title, imageFile) {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('image', imageFile);

    fetch(`${BASE_URL}/update_game_image`, {
        method: 'POST',
        body: formData // Pas besoin de définir Content-Type, il est automatiquement défini avec FormData
    })
    .then(response => {
        if (response.ok) {
            closeImageModal();
            loadGames(); // Recharger la liste des jeux
        } else {
            alert("Erreur lors de la mise à jour de l'image");
        }
    })
    .catch(error => alert('Erreur: ' + error));
}
function addGame(formData) {
    // Afficher la barre de chargement
    document.getElementById('loadingBar').style.display = 'block';
    let loadingProgress = document.getElementById('loadingProgress');
    loadingProgress.style.width = '0%';

    const xhr = new XMLHttpRequest();

    xhr.open("POST", `${BASE_URL}/ajouter_jeu`, true);

    // Gérer les changements d'état de la requête
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) { // La requête est terminée
            if (xhr.status == 200) { // Succès
                loadingProgress.style.width = '100%';
                setTimeout(() => {
                    closeAddGameModal();
                    loadGames(); // Recharger la liste des jeux
                    document.getElementById('loadingBar').style.display = 'none';
                }, 500);
            } else { // Erreur
                alert("Erreur lors de l'ajout du jeu");
                document.getElementById('loadingBar').style.display = 'none';
            }
        }
    };

    // Gérer la progression de l'envoi
    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            loadingProgress.style.width = percentComplete + '%';
        }
    };

    xhr.send(formData);
}

function updateGameDescription(title, description) {
    fetch(`${BASE_URL}/update_game_description`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            description: description
        })
    })
    .then(response => {
        if (response.ok) {
            closeModal();
            loadGames(); // Recharger la liste des jeux
        } else {
            alert('Erreur lors de la mise à jour de la description');
        }
    })
    .catch(error => alert('Erreur: ' + error));
}

function updateGameTitle(oldTitle, newTitle) {
    fetch(`${BASE_URL}/update_game_title`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            old_title: oldTitle, // Assurez-vous que ces clés correspondent à celles attendues par le backend
            new_title: newTitle
        })
    })
    .then(response => {
        if (response.ok) {
            closeTitleModal();
            loadGames(); // Recharger la liste des jeux
        } else {
            console.error('Réponse du serveur non OK');
            response.text().then(text => console.log(text)); // Log pour le débogage
        }
    })
    .catch(error => {
        alert('Erreur: ' + error);
        console.error('Erreur lors de la requête:', error);
    });
}
