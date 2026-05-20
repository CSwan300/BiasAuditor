import React from 'react';
import ReactDOM from 'react-dom/client';
import {App} from './App';
import './styles/globals.css'; // Global styles (grid noise, colors) current all the styles

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);