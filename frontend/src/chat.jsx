import { useState } from 'react'

export default function ChatSection() {
    return (
        <div className="flex flex-col">
            <ChatArea />
            <ChatBox />
        </div>
    )
}

const messages = [];

function ChatBox() {

    const [query, setQuery] = useState('');
    const [answer, setAnswer] = useState('');

    const fetchAnswer = async () => {
        const params = new URLSearchParams({ q: query })
        const response = await fetch(`http://localhost:8000/ask?${params}`)

        if (!response.ok) {
            throw new Error('Network response was not ok')
        }

        const data = await response.json()
        console.log(data)

        setAnswer(data)
    }

    return (
        <div className='flex flex-row w-screen justify-center p-10'>
            <div className='flex flex-col items-end rounded-[20px] w-150 p-5 bg-[#2e2e2e] shadow-gray-700/20 shadow-lg border-1 border-emerald-600/30 border-opacity-30'>
                <textarea 
                    rows='2'
                    placeholder="What do you wanna know?"
                    className='z-0 outline-none field-sizing-content text-gray-100 text-xl resize-none w-[100%] max-h-[300px] font-outfit font-[300]'
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button className="flex flex-col justify-center bg-blue-400 rounded-[50px] hover:bg-orange-500 h-10 w-20 z-10 font-outfit font-[500]" onClick={fetchAnswer}>Enter ➤</button>
            </div>
        </div>
    )
}

function ChatArea() {
    return (
        <div className='min-h-[70vh] h-[80vh] overflow-y-auto'>
            <div className="bg-blue-600 w-100"/>
        </div>
    )
}