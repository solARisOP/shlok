document.addEventListener('DOMContentLoaded', function () {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotBody = document.getElementById('chatbot-body');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Function to toggle the chatbot interface
    chatbotToggle.addEventListener('click', function () {
        chatbotBody.classList.toggle('chatbot-hidden');
    });

    // Function to send a user message and receive a response
    function sendMessage() {
        let userMessage = userInput.value;
        userMessage = userMessage.trim();

        if (userMessage.length) {
            // Create a new message element for the user's message
            const userMessageElement = document.createElement('div');
            userMessageElement.classList.add('user-message');
            userMessageElement.textContent = userMessage;

            // Append the user's message to the chat messages container
            chatbotMessages.appendChild(userMessageElement);

            // Clear the user input field
            userInput.value = '';

            // disabling the input untill the chatbot send a response back
            userInput.disabled = true;

            // Send the user message to your Django backend for processing
            // Replace 'your_django_endpoint' with the actual URL where your backend listens
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch('/chatbot', {
                method: 'POST',
                body: JSON.stringify({ message: userMessage, sessionid: csrfToken }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    // Create a new message element for the chatbot's response

                    const chatbotMessageElement = document.createElement('div');
                    chatbotMessageElement.classList.add('chatbot-message');
                    const lines = data.message.split('\n');
                    lines.forEach(line => {
                        const paragraph = document.createElement('p');
                        paragraph.textContent = line;
                        chatbotMessageElement.appendChild(paragraph);
                    });
                    // Append the chatbot's response to the chat messages container
                    chatbotMessages.appendChild(chatbotMessageElement);

                })
                .catch((error) => {
                    console.error('Error:', error);
                });

            // enabling the input again after sending the response
            userInput.disabled = false;
        }
    }

    // Listen for the "Send" button click
    sendButton.addEventListener('click', sendMessage);

    // Listen for Enter key press in the user input field
    userInput.addEventListener('keyup', function (event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});
