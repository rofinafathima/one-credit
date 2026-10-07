export const API_BASE = 'http://127.0.0.1:8000/api';

export const checkClaim = async (text) => {
  const res = await fetch(`${API_BASE}/fact-check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
};

export const getHistory = async () => {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
};
