// Mets en variable le nom de la salle de chat à partir de l'élément HTML.
const roomName = JSON.parse(document.getElementById('room-name').textContent);

// Généré à l'aide de ChatGPT 4o
// Convertion de la fonction du fichier rsa.py
function strToInt(message) {
    const messageBytes = new TextEncoder().encode(message);
    let mInt = 0n;
    for (let byte of messageBytes) {
        mInt = (mInt << 8n) + BigInt(byte);
    }
    return mInt;
}

// Exponentiation modulaire (python = pow() / non présent dans javascript )
function modularExponentiation(base, exponent, modulus) {
    base = BigInt(base);
    exponent = BigInt(exponent);
    modulus = BigInt(modulus);

    if (modulus === 1n) return 0n;
    let result = 1n;
    base = base % modulus;

    while (exponent > 0n) {
        // If exponent is odd, multiply base with the result
        if (exponent % 2n === 1n) {
            result = (result * base) % modulus;
        }
        // Divide the exponent by 2
        exponent = exponent >> 1n;
        // Square the base
        base = (base * base) % modulus;
    }
    return result;
}

// Convertion de la fonction du fichier rsa.py
function messageEncrypt(m, e, n) {
   return modularExponentiation(m, e, n);
}

// Fonction qui cherche les cookies en lien avec la clée publique et les mets dans des variables
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const esCookie = getCookie('rsa_pub_key_es');
const erCookie = getCookie('rsa_pub_key_er');
const nsCookie = getCookie('rsa_pub_key_ns');
const nrCookie = getCookie('rsa_pub_key_nr');

if (!esCookie || !erCookie || !nsCookie || !nrCookie) {
    console.error("RSA public key cookies are missing or invalid.");
} else {
    const es_rsa = BigInt(esCookie);
    const er_rsa = BigInt(erCookie);
    const ns_rsa = BigInt(nsCookie);
    const nr_rsa = BigInt(nrCookie);

// Fin

// https://dev.to/earthcomfy/django-channels-a-simple-chat-app-part-2-eh9
// Crée une nouvelle instance de WebSocket.
    if (roomName) {
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
            console.log(data)
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

            // Convertir le message en entier
            const mInt = strToInt(message);

            // Chiffrer le message entier
            const encryptedMessageSender = messageEncrypt(mInt, es_rsa, ns_rsa);
            const encryptedMessageReceiver = messageEncrypt(mInt, er_rsa, nr_rsa);

            // Envoie le message au format JSON
            chatSocket.send(JSON.stringify({
                'message_sender': encryptedMessageSender.toString(),
                'message_receiver': encryptedMessageReceiver.toString()
            }));

            // vide l'élement de texte
            messageInputDom.value = '';
        };
    } else {
        console.error("Aucune room name n'a été fourni, la connection Websocket n'est pas établie")
    }
}