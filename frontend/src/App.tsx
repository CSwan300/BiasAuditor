import React from 'react';
import { Header } from "./components/Misc/Header";
import { Footer } from "./components/Misc/Footer";
import { BiasAuditor } from './pages/BiasAuditor';
import { MetricsReference } from './components/Misc/MetricsReference';

export const App: React.FC = () => {
  return (
    <div className="platform-container">
      <Header />

      <main className="content-wrapper">
        <BiasAuditor />
        <MetricsReference />
      </main>

      <Footer />
    </div>
  );
};