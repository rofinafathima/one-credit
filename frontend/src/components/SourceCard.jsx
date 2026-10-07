import React from 'react';

export default function SourceCard({ evidence }) {
  const isSupporting = evidence.evidence_type === "SUPPORTING";
  
  return (
    <div style={{
      background: 'var(--bg-primary)',
      padding: '1rem',
      borderRadius: '8px',
      borderLeft: `4px solid ${isSupporting ? 'var(--verdict-true)' : 'var(--verdict-false)'}`,
      marginBottom: '1rem'
    }}>
      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
        <span style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
          {evidence.publisher || 'Unknown Publisher'}
        </span>
        <span style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
          {evidence.publication_date || 'Publication date unavailable'}
        </span>
      </div>
      <h4 style={{marginBottom: '0.5rem'}}>{evidence.source_title}</h4>
      <p style={{fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem'}}>
        {evidence.snippet}
      </p>
      {evidence.source_url && (
        <a 
          href={evidence.source_url} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{color: 'var(--accent)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: '500'}}
        >
          Open Source →
        </a>
      )}
    </div>
  );
}
