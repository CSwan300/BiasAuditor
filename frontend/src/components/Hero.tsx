export const Hero = () => (
  <section className="hero">
    <div className="hero-inner">
      <h1 className="hero-title">
        Algorithmic Fairness<br/>
        <span className="accent">Intelligence Platform</span>
      </h1>
      <p className="hero-sub">
        Detect, measure, and mitigate bias across protected characteristics.<br/>
        Powered by the Four-Fifths Rule and statistical significance testing.
      </p>
      <div className="hero-pills">
        {['Intersectionality', 'Statistical Significance', 'Equalized Odds', 'PDF Reports'].map(pill => (
          <span key={pill} className="pill">{pill}</span>
        ))}
      </div>
    </div>
  </section>
);