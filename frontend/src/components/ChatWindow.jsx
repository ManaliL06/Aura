import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import { Send, Mic } from 'lucide-react';

const ChatWindow = ({ onCategoryDetect, setActiveCalculator }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: "Good evening. I am AURA. I can assist you with your workout, diet, supplements, muscle gain, fat loss, or calculate your BMI and protein needs. What would you like to focus on?",
      confidence: 100,
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [inputVal, setInputVal] = useState('');
  
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputVal.trim()) return;
    
    // Add user message immediately
    const userMessage = { id: Date.now(), sender: 'user', text: inputVal };
    setMessages(prev => [...prev, userMessage]);
    setInputVal('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.text })
      });
      const data = await res.json();
      
      if (data.category && data.category !== 'rule_based') {
        onCategoryDetect(data.category);
      }
      
      if (data.category === 'rule_based') {
        if (data.answer.toLowerCase().includes('bmi')) setActiveCalculator('bmi');
        else if (data.answer.toLowerCase().includes('protein')) setActiveCalculator('protein');
        else if (data.answer.toLowerCase().includes('calorie')) setActiveCalculator('calorie');
      }
      
      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.answer || "I'm sorry, I couldn't process that request.",
        confidence: data.confidence ? data.confidence * 100 : null,
      };
      
      setIsTyping(false);
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setIsTyping(false);
      setMessages(prev => [...prev, { id: Date.now()+1, sender: 'bot', text: 'Error connecting to the intelligence core.' }]);
    }
  };

  return (
    <div className="flex-1 h-full flex flex-col bg-aura-dark1 relative z-0">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-4/5 h-[300px] bg-aura-gold/5 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="flex-1 overflow-y-auto px-12 pt-16 pb-8 flex flex-col gap-8 scroll-smooth z-10">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isTyping && (
          <div className="flex items-center gap-3 text-aura-gold/80 text-[10px] uppercase tracking-[0.15em] ml-2 animate-pulse mt-2">
            <div className="w-1.5 h-1.5 rounded-full bg-aura-gold"></div>
            Concierge is calculating parameters...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-8 pb-12 z-10 bg-gradient-to-t from-aura-dark1 via-aura-dark1 to-transparent">
        <div className="max-w-3xl mx-auto relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-aura-gold/20 to-white/5 rounded-2xl blur-md opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
          <div className="relative flex items-center bg-aura-dark2 border border-white/10 rounded-2xl p-2 shadow-2xl transition-all duration-300 group-hover:border-aura-gold/30">
            <button className="p-4 text-aura-gold/70 hover:text-aura-gold transition-colors">
              <Mic size={20} />
            </button>
            <input 
              type="text" 
              className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-gray-600 px-2 font-light text-sm"
              placeholder="Inquire with AURA..."
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button 
              onClick={handleSend}
              className="p-3 m-1 bg-gradient-to-r from-aura-gold to-aura-goldLight text-black rounded-xl hover:shadow-[0_0_15px_rgba(212,175,55,0.5)] transition-all duration-300 hover:scale-105"
            >
              <Send size={18} className="ml-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
