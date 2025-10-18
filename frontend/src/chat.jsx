import { useState } from "react";

export default function ChatSection() {
    const [messages, setMessages] = useState([]);

    const handleNewMessage = (message) => {
        setMessages([...messages, { text: message, sender: 'user' }]);
        // Here you can add the logic to get a response from the bot
    };

    return (
        <div className="flex flex-col">
            <ChatArea messages={messages} />
            <ChatBox onSendMessage={handleNewMessage} />
        </div>
    )
}

function ChatBox({ onSendMessage }) {
    const [inputValue, setInputValue] = useState('');

    const handleSend = () => {
        if (inputValue.trim()) {
            onSendMessage(inputValue);
            setInputValue('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className='flex flex-row w-screen justify-center p-10'>
            <div className='flex flex-col items-end rounded-[20px] w-150 p-5 bg-[#2e2e2e] shadow-gray-700/20 shadow-lg border-1 border-emerald-600/30 border-opacity-30'>
                <textarea 
                    rows='2'
                    placeholder="What do you wanna know?"
                    className='z-0 outline-none field-sizing-content text-gray-100 text-xl resize-none w-[100%] max-h-[300px] font-outfit font-[300]'
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button 
                    className="flex flex-col justify-center bg-blue-400 rounded-[50px] hover:bg-orange-500 h-10 w-20 z-10 font-outfit font-[500]"
                    onClick={handleSend}
                >
                    Enter ➤
                </button>
            </div>
        </div>
    )
}

function ChatArea({ messages }) {
    return (
        <div className='min-h-[70vh] h-[80vh] overflow-y-auto flex flex-col-reverse'>
            {messages.slice().reverse().map((message, index) => (
                <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} p-2`}>
                    <div className={`rounded-lg p-3 max-w-lg ${message.sender === 'user' ? 'bg-gray-700 text-white' : 'text-white'}`}>
                        {message.text}
                    </div>
                </div>
            ))}
        </div>
    )
}