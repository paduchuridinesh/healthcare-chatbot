# Hospital Chatbot - React Integration Guide

## API Endpoint

The chatbot backend runs on Flask and exposes a single endpoint:

**Base URL:** `http://localhost:5000` (development)

### POST `/chat`

**Request Format:**
```json
{
  "user_id": "unique_user_identifier",
  "message": "user's message text"
}
```

**Response Format:**
```json
{
  "reply": "Chatbot's response message",
  "decision": "EMERGENCY|CONSULTATION|MINOR|null",
  "dept": "Department name (if applicable)",
  "doctors": ["doctor1", "doctor2"],
  "options": ["Button 1", "Button 2"]
}
```

---

## React Component Example

Here's a sample React component to integrate the chatbot:

```jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [userId] = useState(() => `user_${Date.now()}_${Math.random()}`);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat with greeting
  useEffect(() => {
    setMessages([
      {
        sender: 'bot',
        text: "Hello! I'm your Hospital Guidance Assistant. I'm here to help guide you based on your symptoms. Please describe the main problem or symptom you are experiencing.",
        options: []
      }
    ]);
  }, []);

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    // Add user message to chat
    const userMessage = { sender: 'user', text: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/chat', {
        user_id: userId,
        message: messageText
      });

      const botMessage = {
        sender: 'bot',
        text: response.data.reply,
        decision: response.data.decision,
        dept: response.data.dept,
        doctors: response.data.doctors,
        options: response.data.options || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Sorry, I encountered an error. Please try again.',
        options: []
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleOptionClick = (option) => {
    sendMessage(option);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h3>🏥 Hospital Guidance Assistant</h3>
      </div>

      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="message-content">
              {/* Render markdown-style text */}
              <div dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }} />
              
              {/* Show department link if consultation required */}
              {msg.decision === 'CONSULTATION' && msg.dept && (
                <div className="dept-info">
                  <strong>Department:</strong> {msg.dept}
                  <button 
                    className="book-appointment-btn"
                    onClick={() => window.location.href = '/appointments'}
                  >
                    Book Appointment
                  </button>
                </div>
              )}

              {/* Show doctor list if available */}
              {msg.doctors && msg.doctors.length > 0 && (
                <div className="doctors-list">
                  <strong>Available Doctors:</strong>
                  <ul>
                    {msg.doctors.map((doctor, i) => (
                      <li key={i}>{doctor}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Show quick reply options */}
              {msg.options && msg.options.length > 0 && (
                <div className="quick-options">
                  {msg.options.map((option, i) => (
                    <button
                      key={i}
                      className="option-btn"
                      onClick={() => handleOptionClick(option)}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot">
            <div className="message-content typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chatbot-input-container" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          className="chatbot-input"
        />
        <button type="submit" disabled={isLoading} className="send-btn">
          Send
        </button>
      </form>
    </div>
  );
};

// Helper function to format markdown-style text
const formatMessage = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
    .replace(/\n/g, '<br/>');  // Line breaks
};

export default Chatbot;
```

---

## CSS Styling Example

```css
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  max-width: 500px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: white;
}

.chatbot-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px 10px 0 0;
  text-align: center;
}

.chatbot-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.message {
  margin-bottom: 15px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.message.user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.bot .message-content {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.quick-options {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.option-btn {
  padding: 8px 16px;
  border: 1px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.option-btn:hover {
  background: #667eea;
  color: white;
}

.dept-info {
  margin-top: 10px;
  padding: 10px;
  background: #e8f4fd;
  border-left: 3px solid #2196f3;
  border-radius: 4px;
}

.book-appointment-btn {
  margin-top: 8px;
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.book-appointment-btn:hover {
  background: #1976d2;
}

.doctors-list {
  margin-top: 10px;
  font-size: 0.9rem;
}

.doctors-list ul {
  margin: 5px 0;
  padding-left: 20px;
}

.chatbot-input-container {
  display: flex;
  padding: 15px;
  border-top: 1px solid #ddd;
  background: white;
  border-radius: 0 0 10px 10px;
}

.chatbot-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 25px;
  outline: none;
  font-size: 0.95rem;
}

.chatbot-input:focus {
  border-color: #667eea;
}

.send-btn {
  margin-left: 10px;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #5568d3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 10px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
# Backend (Flask)
pip install flask flask-cors

# Frontend (React)
npm install axios
```

### 2. Start the Backend

```bash
cd d:\Chatbot
python app.py
```

Backend will run on `http://localhost:5000`

### 3. Configure CORS (if needed)

The backend already has CORS enabled via `flask-cors`. If you need to restrict origins:

```python
# In app.py
CORS(app, origins=["http://localhost:3000", "https://yourhospital.com"])
```

### 4. Integrate into React App

1. Copy the `Chatbot` component into your React app
2. Import and use it in your desired page:

```jsx
import Chatbot from './components/Chatbot';

function App() {
  return (
    <div className="App">
      {/* Your other components */}
      <Chatbot />
    </div>
  );
}
```

---

## Key Features

✅ **Emergency Detection** - Immediately identifies life-threatening symptoms  
✅ **Smart Classification** - Categorizes as Emergency/Consultation/Minor  
✅ **Structured Flow** - Duration → Severity → Symptom-specific questions  
✅ **Home Care Tips** - Provides precautions for minor issues  
✅ **Department Routing** - Directs to appropriate specialists  
✅ **Disclaimer** - Shows medical disclaimer once per session  
✅ **Professional Tone** - Calm, no medical jargon  

---

## Production Deployment Notes

1. **Environment Variables**: Use environment variables for API URLs
2. **HTTPS**: Ensure backend uses HTTPS in production
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Analytics**: Track conversation completion rates and emergency detections
5. **Logging**: Log all conversations (anonymized) for quality improvement

---

## Testing Tips

Test these scenarios:
- **Emergency**: "I have severe chest pain and can't breathe"
- **Consultation**: "Moderate headache for 5 days"
- **Minor**: "Mild sore throat since yesterday"
- **Restart**: Say "start over" to test session reset
