import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer>
      <div className="footer-content">
        <p>BIAS AUDITOR — FOR INTERNAL FAIRNESS MONITORING USE ONLY</p>
        <p className="footer-sub">© {new Date().getFullYear()} cswan300</p>
      </div>
    </footer>
  );
};

export default Footer;