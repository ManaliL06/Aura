import React, { useState } from 'react';

const AnalyticsPanel = ({ activeCalculator }) => {
  // BMI State
  const [bmiInputs, setBmiInputs] = useState({ weight: 75, height: 180 });
  const [bmiData, setBmiData] = useState({ bmi: 23.1, category: 'Normal weight' });

  // Protein State
  const [proteinInputs, setProteinInputs] = useState({ weight: 75, activity: 'moderately_active' });
  const [proteinData, setProteinData] = useState({ protein_g: 120 });

  // Calories TDEE State
  const [calInputs, setCalInputs] = useState({
    weight: 75, height: 180, age: 30, gender: 'male', activity: 'moderately_active', goal: 'maintain'
  });
  const [calData, setCalData] = useState({ tdee: 2600, target_calories: 2600 });

  // Compute BMI
  const handleCalcBMI = async () => {
    try {
      const res = await fetch('/api/bmi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ weight_kg: bmiInputs.weight, height_cm: bmiInputs.height })
      });
      const data = await res.json();
      if (!data.error) setBmiData({ bmi: data.bmi, category: data.category });
    } catch(e) {}
  };

  // Compute Protein
  const handleCalcProtein = async () => {
    try {
      const res = await fetch('/api/protein', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ weight_kg: proteinInputs.weight, activity_level: proteinInputs.activity })
      });
      const data = await res.json();
      if (!data.error) setProteinData({ protein_g: data.protein_g });
    } catch(e) {}
  };

  // Compute Calories
  const handleCalcCalories = async () => {
    try {
      const res = await fetch('/api/calorie', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          weight_kg: calInputs.weight, 
          height_cm: calInputs.height,
          age: calInputs.age,
          gender: calInputs.gender,
          activity_level: calInputs.activity,
          goal: calInputs.goal
        })
      });
      const data = await res.json();
      if (!data.error) setCalData({ tdee: data.tdee, target_calories: data.target_calories });
    } catch(e) {}
  };

  // Helper for BMI Bar
  const getBmiPosition = (bmi) => {
    if (bmi < 15) return 0;
    if (bmi > 35) return 100;
    return ((bmi - 15) / 20) * 100;
  };

  // Helper for Calorie Bar Width
  const getCalPosition = (target, tdee) => {
    if (tdee === 0) return 0;
    const ratio = target / tdee;
    if (ratio > 1.2) return 100;
    return (ratio / 1.2) * 100;
  };

  return (
    <aside className="w-96 h-full p-8 flex flex-col gap-6 overflow-y-auto">
      <h2 className="text-aura-gold tracking-[0.2em] text-xs uppercase font-bold mb-2">Biometric Intelligence</h2>

      {/* BMI Tool */}
      <div className="glass-card p-6 border-t border-t-white/10 group hover:border-aura-gold/30">
        <div className="flex justify-between items-start mb-4">
          <span className="text-gray-400 text-[10px] uppercase tracking-widest font-semibold">Body Mass Index</span>
          <span className="bg-aura-gold/10 text-aura-gold px-2 py-0.5 rounded text-[8px] uppercase font-bold tracking-wider border border-aura-gold/20">
            {bmiData.category}
          </span>
        </div>
        
        <div className="flex items-end justify-between mb-4">
          <div className="text-4xl font-serif text-white tracking-tight">{bmiData.bmi}</div>
          <div className="flex flex-col gap-1 w-32">
            <input type="number" 
              className="bg-black/30 border border-white/10 text-white text-[10px] p-1 px-2 rounded outline-none focus:border-aura-gold transition-colors" 
              placeholder="Weight (kg)" 
              value={bmiInputs.weight} 
              onChange={e => setBmiInputs({...bmiInputs, weight: e.target.value})} 
            />
            <input type="number" 
              className="bg-black/30 border border-white/10 text-white text-[10px] p-1 px-2 rounded outline-none focus:border-aura-gold transition-colors" 
              placeholder="Height (cm)" 
              value={bmiInputs.height} 
              onChange={e => setBmiInputs({...bmiInputs, height: e.target.value})} 
            />
            <button onClick={handleCalcBMI} className="bg-aura-gold/20 text-aura-gold text-[10px] font-bold uppercase py-1 rounded hover:bg-aura-gold hover:text-black transition cursor-pointer">Compute</button>
          </div>
        </div>

        <div className="relative h-1 bg-aura-dark4 rounded-full overflow-hidden mt-2">
          <div className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 via-aura-gold to-red-500 w-full opacity-50"></div>
          <div className="absolute top-[-2px] h-2 w-1 bg-white shadow-[0_0_5px_white] transition-all duration-500 ease-out" style={{ left: `${getBmiPosition(bmiData.bmi)}%` }}></div>
        </div>
        <div className="flex justify-between mt-3 text-[9px] text-gray-500 uppercase tracking-wide font-semibold">
          <span>Under</span>
          <span>Normal</span>
          <span>Obese</span>
        </div>
      </div>

      {/* Protein Target Tool */}
      <div className="glass-card p-6 border-t border-t-white/10 group hover:border-aura-gold/30 relative overflow-hidden">
        <div className="relative z-10">
          <div className="text-gray-400 text-[10px] uppercase tracking-widest font-semibold mb-2">Daily Protein Target</div>
          
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-4xl font-serif text-white tracking-tight">{proteinData.protein_g}</span>
            <span className="text-gray-500 text-sm"> g</span>
          </div>

          <div className="flex flex-col gap-2 relative z-20">
             <input type="number" 
               className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold transition-colors w-full"
               placeholder="Weight (kg)"
               value={proteinInputs.weight}
               onChange={e => setProteinInputs({...proteinInputs, weight: e.target.value})}
             />
             <select 
               className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold transition-colors w-full"
               value={proteinInputs.activity}
               onChange={e => setProteinInputs({...proteinInputs, activity: e.target.value})}
             >
               <option value="sedentary">Sedentary</option>
               <option value="lightly_active">Lightly Active</option>
               <option value="moderately_active">Moderately Active</option>
               <option value="very_active">Very Active</option>
               <option value="athlete">Athlete</option>
             </select>
             <button onClick={handleCalcProtein} className="bg-aura-gold/20 text-aura-gold font-bold text-[10px] uppercase py-1.5 rounded hover:bg-aura-gold hover:text-black transition cursor-pointer mt-1">Calculate Target</button>
          </div>
        </div>
        
        {/* Decorative Circle */}
        <div className="absolute -bottom-8 right-0 w-32 h-32 rounded-full border-[3px] border-aura-dark4 border-t-aura-gold border-l-aura-gold rotate-45 blur-[0.5px]"></div>
      </div>

      {/* Active Calorie (TDEE) Tool */}
      {activeCalculator === 'calorie' && (
      <div className="glass-card p-6 border-t border-t-white/10 group hover:border-aura-gold/30">
        <div className="flex justify-between items-center mb-4">
          <span className="text-gray-400 text-[10px] uppercase tracking-widest font-semibold">TDEE Calories</span>
          <span className="bg-aura-gold/10 text-aura-gold px-2 py-0.5 rounded text-[8px] uppercase font-bold tracking-wider border border-aura-gold/20">
            {calInputs.goal.toUpperCase()}
          </span>
        </div>
        
        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-4xl font-serif text-aura-gold tracking-tight drop-shadow-[0_0_8px_rgba(212,175,55,0.4)]">{calData.target_calories}</span>
          <span className="text-gray-500 text-[10px] uppercase tracking-widest">Kcal</span>
        </div>

        <div className="grid grid-cols-2 gap-2 mb-2">
          <input type="number" className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" placeholder="Weight (kg)" value={calInputs.weight} onChange={e => setCalInputs({...calInputs, weight: e.target.value})} />
          <input type="number" className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" placeholder="Height (cm)" value={calInputs.height} onChange={e => setCalInputs({...calInputs, height: e.target.value})} />
        </div>
        <div className="grid grid-cols-2 gap-2 mb-2">
           <input type="number" className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" placeholder="Age" value={calInputs.age} onChange={e => setCalInputs({...calInputs, age: e.target.value})} />
           <select className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" value={calInputs.gender} onChange={e => setCalInputs({...calInputs, gender: e.target.value})}>
             <option value="male">Male</option>
             <option value="female">Female</option>
           </select>
        </div>
        <div className="flex flex-col gap-2 mb-4">
           <select className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" value={calInputs.activity} onChange={e => setCalInputs({...calInputs, activity: e.target.value})}>
             <option value="sedentary">Sedentary</option>
             <option value="lightly_active">Lightly Active</option>
             <option value="moderately_active">Moderately Active</option>
             <option value="very_active">Very Active</option>
             <option value="extra_active">Extra Active</option>
           </select>
           <select className="bg-black/80 border border-white/10 text-white text-[10px] py-1 px-2 rounded outline-none focus:border-aura-gold w-full" value={calInputs.goal} onChange={e => setCalInputs({...calInputs, goal: e.target.value})}>
             <option value="maintain">Maintain Weight</option>
             <option value="lose">Lose Fat (-500 cal)</option>
             <option value="gain">Build Muscle (+300 cal)</option>
           </select>
        </div>
        <button onClick={handleCalcCalories} className="w-full bg-aura-gold/20 text-aura-gold font-bold text-[10px] uppercase py-2 rounded hover:bg-aura-gold hover:text-black transition cursor-pointer">Solve TDEE</button>

      </div>
      )}
    </aside>
  );
};

export default AnalyticsPanel;
