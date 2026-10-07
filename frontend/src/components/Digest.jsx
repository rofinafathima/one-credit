import React, { useState } from 'react';
import { API_BASE } from '../services/api';

export default function Digest() {
  const [topic, setTopic] = useState('technology news');
  const [loading, setLoading] = useState(false);
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setError(null);
    setDigest(null);
    try {
      const res = await fetch(`${API_BASE}/digest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      if (!res.ok) throw new Error('Failed to generate digest');
      const data = await res.json();
      setDigest(data.digest);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card" style={{marginBottom: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>Daily Digest Writer</h2>
        <p style={{marginBottom: '1rem', color: 'var(--text-secondary)'}}>
          Generate a daily digest compiled by the AI agent, saved to the database, and exported as Markdown via MCP tools.
        </p>
        <input 
          type="text"
          placeholder="Topic (e.g., Technology News, Health)"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          style={{marginBottom: '1rem'}}
        />
        <button className="primary" onClick={handleGenerate} disabled={loading}>
          {loading ? (
            <span style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <div className="spinner"></div>
              Generating...
            </span>
          ) : 'Generate Digest'}
        </button>
      </div>

      {error && <div style={{color: 'var(--verdict-false)'}}>Error: {error}</div>}

      {digest && (
        <div className="card">
          <h3 style={{marginBottom: '1rem'}}>Generated Digest</h3>
          <div style={{
            background: 'var(--bg-primary)',
            padding: '1.5rem',
            borderRadius: '8px',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            color: 'var(--text-secondary)'
          }}>
            {digest}
          </div>
        </div>
      )}
    </div>
  );
}
