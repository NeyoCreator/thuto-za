let currentStep = 0;

document.addEventListener('DOMContentLoaded', function() {
    updateStepper(1);
    let initialMessage = "Welcome! What type of website would you like to create?";
    addMessage(initialMessage, "bot-message");
    addSuggestionButtons(["Portfolio/CV", "Blog", "Landing Page"]);
});

// Event listener for user message sending
document.getElementById('send-btn').addEventListener('click', function() {
    const userInput = document.getElementById('user-value');
    const message = userInput.value;
    
    if (message.trim() !== "") {
        addMessage(message, "user-message");
        userInput.value = "";  // Clear input
        toggleLoading(true); // Show loading spinner

        sendMessageToBot(message);
    }
});

// Function to linkify URLs in text
function linkify(text) {
    const urlPattern = /(https?:\/\/[^\s]+)/g;
    return text.replace(
        urlPattern,
        '<a href="$1" target="_blank" style="color: #0000FF; text-decoration: underline; font-weight: bold;">$1</a>'
    );
}

// Function to append messages to the chat window with linkify support
function addMessage(text, sender) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('chat-message', sender === 'user-message' ? 'user-message' : 'bot-message');
    messageContainer.innerHTML = linkify(text);
    document.getElementById('messages').appendChild(messageContainer);
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
            addMessage(suggestion, "user-message");
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
        addMessage(data.message, 'bot-message');
        
        if (data.suggestions && Array.isArray(data.suggestions)) {
            addSuggestionButtons(data.suggestions);
        } else if (data.phase === 4) {
            // For the final question, we'll use a text input instead of buttons
            showTextInput();
        }
        
        if (data.nextStep) {
            updateStepper(data.nextStep);
        }
        
        toggleLoading(false); // Hide loading spinner after response
    })
    .catch(error => {
        console.error('Error:', error);
        toggleLoading(false); // Hide loading spinner on error
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

function toggleLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

// Function to send user instruction to update the website
function updateWebsiteContent(instruction) {
    fetch('/update_website', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ instruction })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.message, 'bot-message');
        refreshPreview(); // Refresh the preview after update
    })
    .catch(error => console.error('Error:', error));
}

// Event listener for user input to update the website
document.getElementById('send-btn').addEventListener('click', function() {
    const userInstruction = document.getElementById('user-value').value;
    addMessage(userInstruction, "user-message");
    updateWebsiteContent(userInstruction);
});

// Function to refresh the iframe preview of the generated website
function refreshPreview() {
    const previewFrame = document.getElementById('preview-frame');
    previewFrame.src = previewFrame.src;
}

