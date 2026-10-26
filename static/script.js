function showUserMessage(message)
{
    const chatBox = document.getElementById("chat-box");
    const userDiv = document.createElement("div");
    userDiv.className = "user-row chat-message";
    userDiv.innerHTML = `
        <div class="user-message-wrapper">
            <div class="sender-name user-name">
                You
            </div>
            <div class="user-bubble">
                ${message}
                <div class="time">
                    ${new Date().toLocaleTimeString()}
                </div>
            </div>
        </div>
        <div class="user-avatar">
            <i class="bi bi-person-fill"></i>
        </div>
    `;
    chatBox.appendChild(userDiv);
    return userDiv;
}

function showThinkingMessage()
{
    const chatBox = document.getElementById("chat-box");
    const thinkingDiv = document.createElement("div");
    thinkingDiv.className = "bot-row chat-message";
    thinkingDiv.innerHTML = `
        <div class="avatar">
            <i class="bi bi-robot"></i>
        </div>
        <div class="message-wrapper">
            <div class="sender-name">
                CUS AI Assistant
            </div>
            <div class="bot-bubble thinking-bubble">
                <span class="thinking-text">
                    Thinking
                </span>
                <span class="thinking-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
            </div>
        </div>
    `;
    chatBox.appendChild(thinkingDiv);
    return thinkingDiv;
}

function showBotMessage(response)
{
    const chatBox = document.getElementById("chat-box");
    const botDiv = document.createElement("div");
    botDiv.className = "bot-row chat-message";
    botDiv.innerHTML = `
        <div class="avatar">
            <i class="bi bi-robot"></i>
        </div>
        <div class="message-wrapper">
            <div class="sender-name">
                CUS AI Assistant
            </div>
            <div class="bot-bubble">
                <div class="bot-response-text">
                    ${response.replace(/\n/g, "<br>")}
                </div>
                <div class="bot-message-actions">
                    <button
                        type="button"
                        class="speak-button"
                        title="Read response aloud"
                        aria-label="Read response aloud"
                        onclick="speakResponse(
                            this,
                            this.closest('.bot-bubble')
                                .querySelector('.bot-response-text')
                                .innerText
                        )">
                        <i class="bi bi-volume-up-fill"></i>
                    </button>
                    <div class="time">
                        ${new Date().toLocaleTimeString()}
                    </div>
                </div>
            </div>
        </div>
    `;
    chatBox.appendChild(botDiv);
    return botDiv;
}
function showErrorMessage()
{
    const chatBox = document.getElementById("chat-box");
    const errorDiv = document.createElement("div");
    errorDiv.className = "bot-row chat-message";
    errorDiv.innerHTML = `
        <div class="avatar">
            <i class="bi bi-robot"></i>
        </div>
        <div class="message-wrapper">
            <div class="sender-name">
                CUS AI Assistant
            </div>
            <div class="bot-bubble">
                <div class="bot-response-text">
                    <i class="bi bi-exclamation-circle"></i>
                    Sorry, I’m unable to process your request right now.
                    <br>
                    Please try again in a moment.
                </div>
                <div class="time">
                    ${new Date().toLocaleTimeString()}
                </div>
            </div>
        </div>
    `;
    chatBox.appendChild(errorDiv);
    return errorDiv;
}
function scrollToMessage(element)
{
    requestAnimationFrame(() => {
        element.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    });
}
async function sendMessage()
{
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (message === "")
        return;
    const sendButton =
        document.querySelector(".send-button");
    const voiceButton =
        document.getElementById("voice-btn");
    showUserMessage(message);
    input.value = "";
    if (sendButton)
    {
        sendButton.disabled = true;
    }
    if (voiceButton)
    {
        voiceButton.disabled = true;
    }
    const selectedLanguage =
        document.getElementById("language-select").value;
    const thinkingDiv =
        showThinkingMessage();
    scrollToMessage(thinkingDiv);
    try
    {
        const response = await fetch("/get_response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                language: selectedLanguage
            })
        });
        if (!response.ok)
        {
            throw new Error(
                `Server returned ${response.status}`
            );
        }
        const data = await response.json();
        if (
            !data ||
            typeof data.response !== "string" ||
            data.response.trim() === ""
        )
        {
            throw new Error(
                "Invalid chatbot response"
            );
        }
        thinkingDiv.remove();
        const botDiv =
            showBotMessage(data.response);

        scrollToMessage(botDiv);

    }
    catch (error)
    {
        console.error(
            "Chatbot error:",
            error
        );
        thinkingDiv.remove();
        const errorDiv =
            showErrorMessage();

        scrollToMessage(errorDiv);
    }
    if (sendButton)
    {
        sendButton.disabled = false;
    }

    if (voiceButton)
    {
        voiceButton.disabled = false;
    }
}
document
    .getElementById("user-input")
    .addEventListener(
        "keypress",
        function(event)
        {
            if (event.key === "Enter")
            {
                sendMessage();
            }
        }
    );
function quickQuestion(text)
{
    document.getElementById("user-input").value = text;
    sendMessage();
}
function clearChat()
{
    const chatBox =
        document.getElementById("chat-box");
    if (!chatBox)
        return;
    chatBox
        .querySelectorAll(
            ".chat-message"
        )
        .forEach(message =>{
            message.remove();
        });
    window.speechSynthesis.cancel();
}

document
    .getElementById("clear-chat-btn")
    .addEventListener(
        "click",
        clearChat
    );
document
    .getElementById("theme-btn")
    .addEventListener(
        "click",
        () =>
        {
            document.body.classList.toggle("dark");
            const icon =
                document.querySelector("#theme-btn i");
            if (
                document.body.classList.contains("dark")
            )
            {
                icon.className =
                    "bi bi-sun-fill";
            }
            else
            {
                icon.className =
                    "bi bi-moon-stars-fill";
            }
        }
    );
const languageSelect =
    document.getElementById("language-select");
const userInput =
    document.getElementById("user-input");
languageSelect.addEventListener(
    "change",
    function()
    {
        const placeholders = {
            en: "Ask your question...",
            ur: "...اپنا سوال پوچھیں",
            hi: "अपना सवाल पूछें..."

        };
        userInput.placeholder =
            placeholders[this.value] ||
            "Ask your question...";
    }
);
const voiceButton =
    document.getElementById("voice-btn");
const inputBox =
    document.getElementById("user-input");
const languageDropdown =
    document.getElementById("language-select");
const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;
if (SpeechRecognition)
{
    const recognition =
        new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
   
    voiceButton.addEventListener(
        "click",
        function()
        {
            const selectedLanguage =
                languageDropdown.value;
            const voiceLanguages = {
                en: "en-IN",
                ur: "ur-IN",
                hi: "hi-IN"
            };
            if (selectedLanguage === "ks")
            {
                alert(
                    "Voice input is currently available for English, Urdu and Hindi."
                );

                return;
            }
            recognition.lang = 
                voiceLanguages[selectedLanguage] ||
                "en-IN";
            recognition.start();
            recognition.onstart = function()
            {
                console.log("Voice recognition started");
                voiceButton.classList.add("recording");
            };
            voiceButton.classList.add(
                "recording"
            );
        }
    );
    recognition.onresult =
        function(event)
        {
            const transcript =
                event.results[0][0].transcript;
            inputBox.value =
                transcript;
            voiceButton.classList.remove(
                "recording"
            );
            inputBox.focus();
        };
    recognition.onerror =
        function(event)
        {
            console.log(
                "Voice input error:",
                event.error
            );
            voiceButton.classList.remove(
                "recording"
            );
        };
    recognition.onend =
        function()
        {
            voiceButton.classList.remove(
                "recording"
            );
        };
}
else
{
    voiceButton.addEventListener(
        "click",
        function()
        {
            alert(
                "Voice input is not supported by this browser. Please use Google Chrome."
            );
        }
    );
}
let currentSpeechButton = null;
function speakResponse(button, text)
{
    if (!("speechSynthesis" in window))
    {
        alert(
            "Voice output is not supported by this browser."
        );
        return;
    }
    const selectedLanguage =
        document.getElementById("language-select").value;
    if (selectedLanguage === "ur")
    {
        alert(
            "Urdu voice output is not available on this device."
        );
        return;
    }
    const icon =
        button.querySelector("i");
    if (
        currentSpeechButton === button && 
        window.speechSynthesis.paused
    )
 
    {
        window.speechSynthesis.resume();
        icon.className =
            "bi bi-pause-fill";
        button.title =
            "Pause speech";
        return;
    }
    if ( 
        currentSpeechButton === button && 
        window.speechSynthesis.speaking 
    )
   
    {
        window.speechSynthesis.pause();
        icon.className =
            "bi bi-play-fill";
        button.title =
            "Resume speech";
        return;
    }
    window.speechSynthesis.cancel();
    currentSpeechButton = button;
    const speechLanguages = {
        en: "en-IN",
        hi: "hi-IN"
    };
    const cleanText =
        text.replace(
            /<[^>]*>/g,
            " "
        );
    const speech =
        new SpeechSynthesisUtterance(
            cleanText
        );
    speech.lang =
        speechLanguages[selectedLanguage] ||
        "en-IN";
    speech.rate = 0.9;
    speech.pitch = 1;
    speech.onstart =
        function()
        {
            icon.className =
                "bi bi-pause-fill";

            button.title =
                "Pause speech";
        };
    speech.onend =
        function()
        {
            icon.className =
                "bi bi-volume-up-fill";
            button.title =
                "Read response aloud";
        };
    speech.onresume = 
        function() 
        { 
            icon.className = "bi bi-pause-fill"; 
            button.title = "Pause speech"; 
        };
    speech.onpause = 
        function() 
        { 
            icon.className = "bi bi-play-fill"; 
            button.title = "Resume speech"; 
        };
    speech.oncancel =
        function()
        {
            icon.className =
                "bi bi-volume-up-fill";
            button.title =
                "Read response aloud";
        
            if (currentSpeechButton === button)
            {
                currentSpeechButton = null;
            }
        };
    speech.onerror =
        function()
        {
            icon.className =
                "bi bi-volume-up-fill";

            button.title =
                "Read response aloud";
        };
    window.speechSynthesis.speak(
        speech
    );
}

