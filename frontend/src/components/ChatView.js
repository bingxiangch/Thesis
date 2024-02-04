import React, { useState } from 'react';
import api from '../common/api'

export const ChatView = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (newMessage.trim() !== '') {
      // Add the user's message to the chat
      setMessages((prevMessages) => [...prevMessages, { text: newMessage, sender: 'user' }]);
      setLoading(true);

      // Make an API call to get a response
      try {
        const response = await api.post('http://localhost:8001/v1/chat', { prompt: newMessage });
        setMessages((prevMessages) => [...prevMessages, { text: response.data.response, sender: 'bot' }]);
      } catch (error) {
        console.error('Error fetching response from the server:', error.message);
      } finally {
        setLoading(false);
      }

      // Clear the input field
      setNewMessage('');
    }
  };

  return (
    <main className="bg-slate-50 p-6 sm:p-10 flex-auto">
      <h1 className="text-xl font-bold text-left mb-4">Chat</h1>
      <div>
        <div style={{ height: '300px', overflowY: 'auto', border: '1px solid #ccc', padding: '10px' }}>
          {messages.map((message, index) => (
            <div key={index} style={{ marginBottom: '10px', textAlign: message.sender === 'user' ? 'right' : 'left' }}>
              <strong>{message.sender === 'user' ? 'You' : 'Bot'}:</strong> {message.text}
            </div>
          ))}
        </div>
        <div className="flex items-center mt-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="border rounded-l py-2 px-4 w-3/4 focus:outline-none"
          />
          <button
            onClick={handleSendMessage}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r focus:outline-none"
            disabled={loading} // Disable button during loading
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </main>
  );
};
