import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/api';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory()
      .then(data => setHistory(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div><div className="spinner"></div> Loading history...</div>;
  }

  if (history.length === 0) {
    return <div className="card">No past fact-checks found.</div>;
  }

  return (
    <div>
      <h2 style={{marginBottom: '2rem'}}>Fact-Check History</h2>
      {history.map((run, i) => (
        <div key={run.verification_id} className="card" style={{marginBottom: '2rem'}}>
          <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem'}}>
            Run ID: {run.verification_id}
          </div>
          {run.claims.map((res, j) => (
            <div key={j} style={{
              background: 'var(--bg-primary)', 
              padding: '1.5rem', 
              borderRadius: '8px',
              marginBottom: '1rem',
              borderLeft: `4px solid var(--verdict-${res.verdict.toLowerCase() === 'true' ? 'true' : res.verdict.toLowerCase() === 'false' ? 'false' : res.verdict.toLowerCase() === 'misleading' ? 'misleading' : 'unverifiable'})`
            }}>
              <h4 style={{marginBottom: '1rem'}}>{res.claim}</h4>
              <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                <span className={`verdict-badge verdict-${res.verdict}`}>{res.verdict}</span>
                <span style={{color: 'var(--text-secondary)', fontSize: '0.875rem'}}>
                  Checked: {new Date(res.checked_at).toLocaleString()}
                </span>
              </div>
              <p style={{fontSize: '0.9rem', color: 'var(--text-secondary)'}}>
                {res.summary}
              </p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
