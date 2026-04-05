import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import AnalyticsPanel from './components/AnalyticsPanel';

function App() {
  const [activeCategory, setActiveCategory] = useState('');
  const [activeCalculator, setActiveCalculator] = useState('');

  return (
    <div className="h-screen w-full bg-aura-dark1 flex overflow-hidden font-sans text-gray-200">
      
      {/* 1. Left Navigation */}
      <Sidebar activeCategory={activeCategory} />

      {/* Center & Right Wrapper */}
      <div className="flex-1 flex flex-col relative">
        
        {/* Top bar area removed by user request */}

        {/* Dynamic Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* 2. Main Chat */}
          <ChatWindow 
            onCategoryDetect={setActiveCategory} 
            setActiveCalculator={setActiveCalculator} 
          />
          
          {/* 3. Analytics Panel */}
          <div className="bg-aura-dark1 z-10 border-l border-white/5 relative shadow-[-20px_0_30px_rgba(0,0,0,0.5)]">
            <AnalyticsPanel activeCalculator={activeCalculator} />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
