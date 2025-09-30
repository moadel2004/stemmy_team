// Chatbot-UI/speechService.js

function initializeSpeechRecognition(onResultCallback, onErrorCallback, onEndCallback) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn('Speech Recognition API not supported in this browser.');
        alert("Speech recognition is not supported in this browser.");
        return null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }
        if (onResultCallback) {
            onResultCallback(finalTranscript, interimTranscript);
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        if (onErrorCallback) {
            onErrorCallback(event.error);
        }
    };

    recognition.onend = () => {
        if (onEndCallback) {
            onEndCallback();
        }
    };

    return recognition;
}

// MODIFICATION: Added a 'clearInput' parameter to control clearing the text field.
function startRecording(recognitionInstance, setInputValueCallback, clearInput = true) {
    if (recognitionInstance) {
        // MODIFICATION: Only clear the input if requested.
        if (setInputValueCallback && clearInput) {
            setInputValueCallback(''); // Clear input field before starting
        }
        recognitionInstance.start();
        console.log('Speech recognition started...');
        return true;
    }
    return false;
}

function stopRecording(recognitionInstance) {
    if (recognitionInstance) {
        recognitionInstance.stop();
        console.log('Speech recognition stopped.');
        return true;
    }
    return false;
}