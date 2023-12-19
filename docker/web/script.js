document.addEventListener('DOMContentLoaded', function() {
    chargerJeux();
});

function chargerJeux() {
    fetch('xml/jeux.xml')
        .then(response => response.text())
        .then(data => {
            let parser = new DOMParser();
            let xml = parser.parseFromString(data, "application/xml");
            afficherJeux(xml);
        });
}

function afficherJeux(xml) {
    let jeux = xml.getElementsByTagName('jeu');
    let listeJeux = document.getElementById('listeJeux');

    for (let jeu of jeux) {
        let titre = jeu.getElementsByTagName('titre')[0].textContent;
        let descriptif = jeu.getElementsByTagName('descriptif')[0].textContent;
        let image = jeu.getElementsByTagName('image')[0].textContent;
        let torrent = jeu.getElementsByTagName('torrent')[0].textContent;

        let jeuDiv = document.createElement('div');
        jeuDiv.className = 'jeu';
        jeuDiv.innerHTML = `
            <a href="torrent/${torrent}" target="_blank">
                <img src="data/${titre}/${image}" alt="${titre}">
            </a>
            <h2>${titre}</h2>
            <p>${descriptif}</p>
        `;
        listeJeux.appendChild(jeuDiv);
    }
}
