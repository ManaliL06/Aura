import React from 'react';

const MessageBubble = ({ message }) => {
  const isBot = message.sender === 'bot';

  return (
    <div className={`flex flex-col w-full max-w-3xl ${isBot ? 'items-start' : 'items-end ml-auto'}`}>
      
      {/* The Bubble */}
      <div 
        className={`p-6 text-sm leading-relaxed tracking-wide shadow-2xl relative ${
          isBot 
            ? 'bg-aura-dark3 border border-white/5 text-gray-200 rounded-[28px] rounded-bl-xl hover:border-aura-gold/20 hover:shadow-[0_0_20px_rgba(212,175,55,0.05)] transition-all duration-500' 
            : 'bg-aura-dark2 border border-white/5 text-gray-300 rounded-[28px] rounded-br-[4px] border-r-aura-gold'
        }`}
      >
        {isBot && (
          <div className="absolute -inset-[1px] bg-gradient-to-br from-white/10 to-transparent rounded-[28px] rounded-bl-xl opacity-20 pointer-events-none"></div>
        )}
        <div className="relative z-10">{message.text}</div>
      </div>

      {/* Bot Confidence Meta */}
      {isBot && message.confidence && (
        <div className="flex items-center gap-2 mt-4 ml-4">
          <span className="text-aura-gold text-[9px] uppercase tracking-[0.2em] font-bold">
            Aura Intel • {message.confidence.toFixed(1)}% Confidence
          </span>
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
