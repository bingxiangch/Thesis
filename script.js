let accessToken; // Store the access token

document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const tokenResponse = await fetch('http://localhost:8001/v1/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (!tokenResponse.ok) {
            throw new Error(`Error: ${tokenResponse.status}`);
        }

        const tokenData = await tokenResponse.json();
        accessToken = tokenData.access_token; // Store the access token
        document.getElementById('chatForm').style.display = 'block'; // Show chat form

    } catch (error) {
        console.error('An error occurred:', error);
    }
});

document.getElementById('chatForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const message = document.getElementById('chatInput').value;
    try {
        const chatResponse = await fetch('http://localhost:8001/v1/chat', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: message })
        });

        if (!chatResponse.ok) {
            throw new Error(`Error: ${chatResponse.status}`);
        }

        const chatData = await chatResponse.json();
        displayChatMessage(chatData);
        // document.getElementById('chatInput').value = ''; // Clear the input field
    } catch (error) {
        console.error('An error occurred:', error);
    }
});

function displayDocuments(documents) {
    const documentsDiv = document.getElementById('documents');
    documentsDiv.innerHTML = '';

    documents.forEach(document => {
        const documentDiv = document.createElement('div');
        documentDiv.textContent = `Title: ${document.title}, Content: ${document.content}`;
        documentsDiv.appendChild(documentDiv);
    });
}

function displayChatMessage(chatData) {
    const chatOutput = document.getElementById('chatOutput');
    const chatMessageDiv = document.createElement('div');
    chatMessageDiv.textContent = chatData.response; // Assuming the response has a 'response' field
    chatOutput.appendChild(chatMessageDiv);
}
