const { useState, useEffect, useRef } = React;

// Scientific symbols for background
const scientificSymbols = [
    'N', 'β', 'Ω', 'O₂', 'W', '°C', 'tan(θ)', 'H₂', 'e^x', 'J', 'x²⁰',
    '∑', '∫', '∂', '∆', '∇', '∞', 'π', 'α', 'γ', 'θ', 'λ', 'μ', 'σ',
    '√', '∛', '≤', '≥', '≠', '≈', '≡', '∝', '∴', '∵', '∠', '⊥', '∥',
    'CO₂', 'H₂O', 'NaCl', 'CH₄', 'NH₃', 'Fe²⁺', 'Ca²⁺', 'SO₄²⁻'
];

// Floating background symbols component
const FloatingSymbols = () => {
    const [symbols, setSymbols] = useState([]);

    useEffect(() => {
        const createSymbol = () => ({
            id: Math.random(),
            symbol: scientificSymbols[Math.floor(Math.random() * scientificSymbols.length)],
            left: Math.random() * 100,
            animationDelay: Math.random() * 20,
            fontSize: Math.random() * 1.5 + 1.5,
            duration: Math.random() * 10 + 15
        });

        const initialSymbols = Array.from({ length: 50 }, createSymbol);
        setSymbols(initialSymbols);

        const interval = setInterval(() => {
            setSymbols(prev => {
                const newSymbol = createSymbol();
                const updatedSymbols = [...prev, newSymbol];
                return updatedSymbols.slice(-60);
            });
        }, 1500);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-symbols">
            {symbols.map(symbol => (
                <div
                    key={symbol.id}
                    className="floating-symbol"
                    style={{
                        left: `${symbol.left}%`,
                        animationDelay: `${symbol.animationDelay}s`,
                        fontSize: `${symbol.fontSize}rem`,
                        animationDuration: `${symbol.duration}s`
                    }}
                >
                    {symbol.symbol}
                </div>
            ))}
        </div>
    );
};

// Interactive SVG Character (can be used as AI Avatar)
// You should replace the content of this SVG with your actual STEMMY.svg data
const InteractiveSVGCharacter = ({ className }) => {
    // Example SVG - REPLACE THIS with your actual SVG code
    return (
        <svg viewBox="0 0 100 100" className={className || "ai-avatar-svg"}>
            <circle cx="50" cy="50" r="40" fill="#4285f4" /> {/* Example: Blue circle */}
            <circle cx="40" cy="40" r="5" fill="white" /> {/* Example: Left eye */}
            <circle cx="60" cy="40" r="5" fill="white" /> {/* Example: Right eye */}
            <path d="M40 60 Q50 70 60 60" stroke="white" strokeWidth="3" fill="transparent" /> {/* Example: Smile */}
            {/* For your STEMMY.svg, you would copy its <path>, <circle>, etc. elements here */}
            {/* Make sure the viewBox matches your SVG's viewBox */}
        </svg>
    );
};


// Message component
const Message = ({ message, isUser }) => (
    <div className={`message ${isUser ? 'user' : 'ai'}`}>
        <div className={`message-avatar ${isUser ? 'user' : 'ai'}`}>
            {isUser ? 'You' : <InteractiveSVGCharacter />}
        </div>
        <div className="message-content">
            {message}
        </div>
    </div>
);

// Typing indicator component
const TypingIndicator = () => (
    <div className="typing-indicator">
        <div className="message-avatar ai">
            <InteractiveSVGCharacter />
        </div>
        <div className="typing-content">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
        </div>
    </div>
);

// Main App Component
const STEMTutorApp = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            content: "Hey! How can I help you today? 😊",
            isUser: false
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    // Removed showInteractiveSVG state and related useEffect
    const messagesEndRef = useRef(null);
    // Removed inputAreaRef if no longer needed for SVG positioning logic

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    // Removed useEffect for showing/hiding interactive SVG in input area

    const generateAIResponse = (userMessage) => {
        const responses = [
            "That's an interesting question! Could you provide more details about what you're studying in STEM, so I can give you the best help?",
            "Great question! Let me break this down for you step by step.",
            "I'd be happy to help you with that! Can you tell me more about the specific concept you're working on?",
            "Excellent! This is a fundamental concept in STEM. Let me explain it in a way that's easy to understand.",
            "Perfect question for learning! Let's explore this topic together."
        ];
        
        if (userMessage.toLowerCase().includes('math') || userMessage.toLowerCase().includes('equation')) {
            return "Math is fascinating! What specific mathematical concept would you like to explore? I can help with algebra, calculus, geometry, statistics, and more.";
        }
        
        if (userMessage.toLowerCase().includes('science') || userMessage.toLowerCase().includes('chemistry') || userMessage.toLowerCase().includes('physics')) {
            return "Science is amazing! Whether it's physics, chemistry, biology, or earth science, I'm here to help you understand the concepts. What are you curious about?";
        }
        
        if (userMessage.toLowerCase().includes('code') || userMessage.toLowerCase().includes('programming')) {
            return "Programming is a powerful skill! I can help you with various programming languages, algorithms, data structures, and computer science concepts. What would you like to learn?";
        }
        
        return responses[Math.floor(Math.random() * responses.length)];
    };

    const handleSendMessage = () => {
        if (inputValue.trim()) {
            const userMessage = {
                id: Date.now(),
                content: inputValue,
                isUser: true
            };

            setMessages(prev => [...prev, userMessage]);
            const currentInput = inputValue;
            setInputValue('');
            setIsTyping(true);
            // setShowInteractiveSVG(false); // No longer needed

            setTimeout(() => {
                const aiResponse = {
                    id: Date.now() + 1,
                    content: generateAIResponse(currentInput),
                    isUser: false
                };
                setMessages(prev => [...prev, aiResponse]);
                setIsTyping(false);
            }, 1500 + Math.random() * 1000);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const toggleRecording = () => {
        setIsRecording(!isRecording);
        if (!isRecording) {
            console.log('Started recording...');
            // Add speech recognition logic here
        } else {
            console.log('Stopped recording...');
            // Process recorded audio here
        }
    };

    const handleCameraToggle = () => {
        console.log('Camera toggled');
        // Add actual webcam logic here (e.g., accessing navigator.mediaDevices.getUserMedia)
    };

    return (
        <>
            <FloatingSymbols />
            <div className="app-container">
                <header className="header">
                    <div className="header-icon">S</div>
                    <div className="header-title">STEM Tutor</div>
                </header>

                <div className="chat-container">
                    <div className="messages-area">
                        {messages.map(message => (
                            <Message
                                key={message.id}
                                message={message.content}
                                isUser={message.isUser}
                            />
                        ))}
                        {isTyping && <TypingIndicator />}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Removed InteractiveSVGCharacter from here */}
                    <div className="input-area"> {/* Removed ref={inputAreaRef} if not used */}
                        <div className="input-container">
                            <div className="input-wrapper">
                                <input
                                    type="text"
                                    className="input-field"
                                    placeholder="Ask anything"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                />
                                <div className="input-buttons">
                                    <button
                                        className="input-button camera-button"
                                        onClick={handleCameraToggle}
                                        aria-label="Toggle camera"
                                    >
                                        {/* Updated Camera Icon - more relevant */}
                                        <svg className="icon" viewBox="0 0 24 24">
                                            <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4zM15 16H5V8h10v8zm-6-1h2v-2h-2v2z"/>
                                        </svg>
                                    </button>
                                    <button
                                        className={`input-button ${isRecording ? 'mic-active' : ''}`}
                                        onClick={toggleRecording}
                                        aria-label="Voice input"
                                    >
                                        <svg className="icon" viewBox="0 0 24 24">
                                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.49 6-3.31 6-6.72h-1.7z"/>
                                        </svg>
                                    </button>
                                    <button
                                        className="input-button send"
                                        onClick={handleSendMessage}
                                        disabled={!inputValue.trim() || isTyping}
                                        aria-label="Send message"
                                    >
                                        <svg className="icon" viewBox="0 0 24 24">
                                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

// Render the app
ReactDOM.render(<STEMTutorApp />, document.getElementById('root'));