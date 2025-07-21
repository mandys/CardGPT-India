import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/globals.css';

// Simple landing page until we can figure out the import issue
const App: React.FC = () => {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '3rem',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        textAlign: 'center',
        maxWidth: '600px'
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          borderRadius: '20px',
          margin: '0 auto 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '2rem'
        }}>
          💳
        </div>
        <h1 style={{
          fontSize: '2.5rem',
          margin: '0 0 1rem',
          color: '#1a1a1a'
        }}>
          CardGPT India
        </h1>
        <p style={{
          fontSize: '1.2rem',
          color: '#666',
          lineHeight: '1.6',
          margin: '0 0 2rem'
        }}>
          AI-Powered Credit Card Assistant for Indian Credit Cards
        </p>
        <div style={{
          background: '#f8f9fa',
          padding: '1.5rem',
          borderRadius: '12px',
          margin: '2rem 0'
        }}>
          <h3 style={{ margin: '0 0 1rem', color: '#333' }}>🚧 Temporary Notice</h3>
          <p style={{ margin: '0', color: '#666', fontSize: '1rem' }}>
            We're currently resolving deployment issues. The full application will be restored shortly.
            <br />
            <br />
            <strong>Features Coming Soon:</strong>
            <br />• Compare Axis Atlas, HSBC Premier, and ICICI EPM
            <br />• AI-powered reward calculations
            <br />• Smart spending recommendations
          </p>
        </div>
        <div style={{
          fontSize: '0.9rem',
          color: '#888'
        }}>
          Built with React + TypeScript + FastAPI
        </div>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals