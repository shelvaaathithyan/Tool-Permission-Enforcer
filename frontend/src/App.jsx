import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState('Checking...')

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${url}/health`);
        if (response.ok) {
          const data = await response.json();
          setHealth(`Healthy (${data.status})`);
        } else {
          setHealth('Unavailable (Error Status)');
        }
      } catch (error) {
        setHealth('Unavailable (Network Error)');
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Tool Permission Enforcer</h1>
        <div className="status">
          <p>Backend Status: {health}</p>
        </div>
      </header>
    </div>
  )
}

export default App
