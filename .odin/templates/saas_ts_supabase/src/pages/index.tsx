// src/pages/index.tsx
import React from 'react';
import { supabase } from '../lib/initSupabase';

export default function Home() {
  const handleLogin = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'github'
      });
      if (error) console.error('Login error:', error);
    } catch (err) {
      console.error('Unexpected error:', err);
    }
  };

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>SaaS App with Supabase</h1>
      <p>Welcome to your Next.js + Supabase boilerplate!</p>
      <button onClick={handleLogin} style={{ 
        padding: '1rem 2rem', 
        fontSize: '1rem',
        backgroundColor: '#0070f3',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        Login with GitHub
      </button>
    </div>
  );
}
