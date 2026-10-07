import React, { useState } from 'react';
import FactChecker from './components/FactChecker';
import History from './components/History';
import Digest from './components/Digest';

function App() {
  const [currentTab, setCurrentTab] = useState('check');

  return (
    <div className="app-container">
      <header>
        <div className="logo">
          <span>AI</span> FactChecker
        </div>
        <nav>
          <button 
            className={currentTab === 'check' ? 'active' : ''} 
            onClick={() => setCurrentTab('check')}
          >
            Fact Check
          </button>
          <button 
            className={currentTab === 'history' ? 'active' : ''} 
            onClick={() => setCurrentTab('history')}
          >
            History
          </button>
          <button 
            className={currentTab === 'digest' ? 'active' : ''} 
            onClick={() => setCurrentTab('digest')}
          >
            Daily Digest
          </button>
        </nav>
      </header>
      
      <main>
        {currentTab === 'check' ? <FactChecker /> : 
         currentTab === 'history' ? <History /> : 
         <Digest />}
      </main>
    </div>
  );
}

export default App;
