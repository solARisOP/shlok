window.onresize = ()=>{
    var chatbotToggle = document.getElementById("chatbot-toggle");
    var chatbotContainer = document.getElementById('chatbot-container');
    if(window.innerWidth<=486){
        chatbotToggle.style.bottom = "20px";
        chatbotToggle.style.right = "0px";
        chatbotToggle.style.left = "0px";
        chatbotToggle.style.marginRight = "auto";
        chatbotToggle.style.marginLeft = "auto";

        chatbotContainer.style.bottom = "90px";
        chatbotContainer.style.right = "0px";
        chatbotContainer.style.left = "0px";
        chatbotContainer.style.marginRight = "auto";
        chatbotContainer.style.marginLeft = "auto";
    }
    else{
        chatbotToggle.style.bottom = "80px";
        chatbotToggle.style.marginLeft = "";
        chatbotToggle.style.marginright = "";
        chatbotToggle.style.right = "10px";
        chatbotToggle.style.left = "";

        chatbotContainer.style.bottom = "20px";
        chatbotContainer.style.marginLeft = "";
        chatbotContainer.style.marginright = "";
        chatbotContainer.style.right = "85px";
        chatbotContainer.style.left = "";
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotBody = document.getElementById('chatbot-body');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    if(window.innerWidth<=486){
        chatbotToggle.style.bottom = "20px";
        chatbotToggle.style.right = "0px";
        chatbotToggle.style.left = "0px";
        chatbotToggle.style.marginRight = "auto";
        chatbotToggle.style.marginLeft = "auto";

        chatbotContainer.style.bottom = "90px";
        chatbotContainer.style.right = "0px";
        chatbotContainer.style.left = "0px";
        chatbotContainer.style.marginRight = "auto";
        chatbotContainer.style.marginLeft = "auto";
    }

    // Function to toggle the chatbot interface
    var chatbotVisible = 1
    chatbotToggle.addEventListener('click', function () {
        if(chatbotVisible)
        {
            chatbotContainer.style.display = 'block'
        }
        else{
            chatbotContainer.style.display = 'none'
        }
        chatbotVisible = !chatbotVisible
    });

    // Function to send a user message and receive a response
    function scrollmessages() {
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

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
            scrollmessages();
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
                .then((response) => {
                    console.log(response)
                    return response.json()
                })
                .then((data) => {
                    // Create a new message element for the chatbot's response

                    const chatbotMessageElement = document.createElement('div');
                    chatbotMessageElement.classList.add('chatbot-message');
                    const lines = data.message.split('\n');
                    lines.forEach(line => {
                        const paragraph = document.createElement('p');
                        paragraph.classList.add('parax');
                        paragraph.textContent = line;
                        chatbotMessageElement.appendChild(paragraph);
                    });
                    // Append the chatbot's response to the chat messages container
                    chatbotMessages.appendChild(chatbotMessageElement);
                    scrollmessages();

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
