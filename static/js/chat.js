// Mets en variable le nom de la salle de chat à partir de l'élément HTML.
const roomName = JSON.parse(document.getElementById('room-name').textContent);

// Crée une nouvelle instance de WebSocket.
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

// Converti le message JSON en objet JavaScript, puis examine et agit sur son contenu.
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#chat-log').value += (data.message + '\n');
};

// Affiche un message si la connexion WebSocket si elle est fermée inopinément.
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // touche entrer
        document.querySelector('#chat-message-submit').click();
    }
};

// Selectionne l'élément HTML avec l'id chat-message-submit et envoie un message au serveur quand l'element est cliqué.
document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;

    // Envoie le message au format JSON
    chatSocket.send(JSON.stringify({
        'message': message
    }));

    // Blank the text input element, ready to receive the next line of text from the user.
    messageInputDom.value = '';
};