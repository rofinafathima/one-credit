import React, { useState } from 'react';
import { checkClaim } from '../services/api';
import SourceCard from './SourceCard';

export default function FactChecker() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleCheck = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await checkClaim(text);
      setResults(data.claims);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card" style={{marginBottom: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>AI FACT CHECKER</h2>
        <textarea 
          rows="5"
          placeholder="Paste a claim or forwarded message..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{marginBottom: '1rem'}}
        />
        <button className="primary" onClick={handleCheck} disabled={loading}>
          {loading ? (
            <span style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <div className="spinner"></div>
              Analyzing claims...
            </span>
          ) : 'Verify Claim'}
        </button>
      </div>

      {error && (
        <div style={{color: 'var(--verdict-false)', marginBottom: '1rem'}}>
          Error: {error}
        </div>
      )}

      {results && results.map((res, i) => (
        <div key={i} className="card" style={{marginBottom: '2rem'}}>
          <h3 style={{marginBottom: '1rem', borderBottom: '1px solid var(--bg-primary)', paddingBottom: '0.5rem'}}>
            Claim: {res.claim}
          </h3>
          
          <div style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem'}}>
            <div>
              <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem'}}>VERDICT</div>
              <div className={`verdict-badge verdict-${res.verdict}`}>{res.verdict}</div>
            </div>
            <div>
              <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem'}}>CONFIDENCE</div>
              <div style={{fontWeight: '600'}}>{res.confidence}</div>
            </div>
          </div>
          
          <div style={{marginBottom: '1.5rem'}}>
            <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem'}}>WHY?</div>
            <p>{res.reasoning}</p>
          </div>
          
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
            <div>
              <h4 style={{marginBottom: '1rem', color: 'var(--verdict-true)'}}>SUPPORTING EVIDENCE</h4>
              {res.supporting_evidence.length === 0 ? <p style={{color: 'var(--text-secondary)'}}>No supporting evidence found.</p> : null}
              {res.supporting_evidence.map((ev, idx) => <SourceCard key={idx} evidence={ev} />)}
            </div>
            <div>
              <h4 style={{marginBottom: '1rem', color: 'var(--verdict-false)'}}>CONTRADICTING EVIDENCE</h4>
              {res.contradicting_evidence.length === 0 ? <p style={{color: 'var(--text-secondary)'}}>No contradicting evidence found.</p> : null}
              {res.contradicting_evidence.map((ev, idx) => <SourceCard key={idx} evidence={ev} />)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
