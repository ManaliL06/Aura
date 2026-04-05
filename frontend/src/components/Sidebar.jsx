import React from 'react';
import { Dumbbell, Utensils, Flame, Activity, Pill, Shield } from 'lucide-react';

const Sidebar = ({ activeCategory }) => {
  const menuItems = [
    { id: 'workout', icon: <Dumbbell size={18} />, label: 'Workout' },
    { id: 'diet', icon: <Utensils size={18} />, label: 'Diet' },
    { id: 'fat_loss', icon: <Flame size={18} />, label: 'Fat Loss' },
    { id: 'muscle_gain', icon: <Activity size={18} />, label: 'Muscle Gain' },
    { id: 'supplements', icon: <Pill size={18} />, label: 'Supplements' },
    { id: 'injury_prevention', icon: <Shield size={18} />, label: 'Injury Prevention' },
  ];

  return (
    <aside className="w-64 h-full glass-panel flex flex-col justify-between border-r border-white/5 relative z-10">
      <div>
        <div className="p-8">
          <h1 className="text-3xl font-serif font-bold text-gradient tracking-wider">AURA</h1>
        </div>

        <nav className="mt-4">
          <ul className="space-y-1">
            {menuItems.map((item, idx) => {
              const isActive = item.id === activeCategory;
              return (
                <li key={idx} className="relative">
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-aura-gold rounded-r-full shadow-[0_0_10px_rgba(212,175,55,0.5)]"></div>
                  )}
                  <button 
                    className={`w-full flex items-center gap-4 px-8 py-4 text-sm transition-all duration-300 ${
                      isActive 
                        ? 'text-aura-gold bg-gradient-to-r from-aura-gold/10 to-transparent' 
                        : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                    }`}
                  >
                    <span className={isActive ? 'text-aura-gold' : 'text-gray-500'}>{item.icon}</span>
                    <span className="font-medium tracking-wide">{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
