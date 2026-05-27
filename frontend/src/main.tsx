import React from 'react';
import ReactDOM from 'react-dom/client';
import {App} from './App';
// This is currently all the css
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);