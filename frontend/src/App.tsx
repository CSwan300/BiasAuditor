import React from 'react';
import { Header } from "./components/Misc/Header"; // Path updated
import { Footer } from "./components/Misc/Footer"; // Path updated
import { BiasAuditor } from './pages/BiasAuditor';

export const App: React.FC = () => {
  return (
    <div className="platform-container">
      <Header />

      <div className="content-wrapper">
        <BiasAuditor />
      </div>

      <Footer />
    </div>
  );
};