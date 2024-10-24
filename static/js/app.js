let currentStep = 0;

document.addEventListener('DOMContentLoaded', function() {
    updateStepper(1);
    let initialMessage = "Welcome! What type of website would you like to create?";
    appendMessage(initialMessage, "bot-message");
    addSuggestionButtons(["Portfolio/CV", "Blog", "Landing Page"]);
});

// Event listener for user message sending
document.getElementById('send-btn').addEventListener('click', function() {
    let message = document.getElementById('user-input').value;
    if (message.trim() !== "") {
        appendMessage(message, "user-message");
        sendMessageToBot(message);
        document.getElementById('user-input').value = "";  // Clear input
    }
});

// Function to append messages to the chat window
function appendMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', className);
    messageDiv.textContent = text;
    document.getElementById('messages').appendChild(messageDiv);
    document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
}

// New function to create and display suggestion buttons
function addSuggestionButtons(suggestions) {
    const buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('suggestion-buttons');
    
    suggestions.forEach(suggestion => {
        const button = document.createElement('button');
        button.textContent = suggestion;
        button.addEventListener('click', function() {
            // Toggle 'selected' class on clicked button
            this.classList.toggle('selected');
            appendMessage(suggestion, "user-message");
            sendMessageToBot(suggestion);
        });
        buttonsContainer.appendChild(button);
    });
    
    document.getElementById('messages').appendChild(buttonsContainer);
    document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
}

// Function to send user message to the bot (to be replaced with actual bot logic)
function sendMessageToBot(message) {
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            user_id: '12345',  // Example user ID
            step: currentStep
        })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.message, 'bot-message');
        
        if (data.suggestions && Array.isArray(data.suggestions)) {
            addSuggestionButtons(data.suggestions);
        } else if (data.phase === 4) {
            // For the final question, we'll use a text input instead of buttons
            showTextInput();
        }
        
        if (data.nextStep) {
            updateStepper(data.nextStep);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateStepper(step) {
    currentStep = step;
    document.querySelectorAll('.step').forEach((el, index) => {
        if (index + 1 < step) {
            el.classList.add('completed');
            el.classList.remove('active');
        } else if (index + 1 === step) {
            el.classList.add('active');
            el.classList.remove('completed');
        } else {
            el.classList.remove('active', 'completed');
        }
    });
}

function showTextInput() {
    const inputArea = document.getElementById('input-area');
    inputArea.style.display = 'flex';
    const userInput = document.getElementById('user-input');
    userInput.focus();
}
