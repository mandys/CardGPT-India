import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/globals.css';
// import App from './App';

// Temporary test component to debug Vercel issue
const App = () => {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>CardGPT - Temporary Fix</h1>
      <p>Testing Vercel deployment - will restore full app once working</p>
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