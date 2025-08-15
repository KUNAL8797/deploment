import React from 'react';

interface HomePageProps {
  onGetStarted: () => void;
}

const HomePage: React.FC<HomePageProps> = ({ onGetStarted }) => {
  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-badge">
              <span className="badge-icon">✨</span>
              Powered by Gemini 2.5 Pro
            </div>
            <h1 className="hero-title">
              Transform Your Ideas Into
              <span className="gradient-text"> Investor-Ready Pitches</span>
            </h1>
            <p className="hero-subtitle">
              IdeaForge AI uses advanced artificial intelligence to refine your startup concepts, 
              generate professional business pitches, and provide comprehensive market analysis in seconds.
            </p>
            <div className="hero-actions">
              <button onClick={onGetStarted} className="btn-primary btn-hero">
                <span>Start Building</span>
                <span className="btn-icon">🚀</span>
              </button>
              <button onClick={scrollToFeatures} className="btn-secondary btn-hero">
                <span>Learn More</span>
              </button>
            </div>
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">10K+</span>
                <span className="stat-label">Ideas Enhanced</span>
              </div>
              <div className="stat">
                <span className="stat-number">95%</span>
                <span className="stat-label">Success Rate</span>
              </div>
              <div className="stat">
                <span className="stat-number">AI-Powered</span>
                <span className="stat-label">Analysis</span>
              </div>
            </div>
          </div>
          <div className="hero-visual">
            <div className="idea-transformation">
              <div className="before-card">
                <div className="card-header">💭 Raw Idea</div>
                <div className="card-content">"A food delivery app for my city..."</div>
              </div>
              <div className="transform-arrow">
                <div className="arrow-circle">
                  <span>🤖</span>
                </div>
              </div>
              <div className="after-card">
                <div className="card-header">🚀 Professional Pitch</div>
                <div className="card-content">
                  <strong>EcoEats:</strong> Sustainable food delivery platform connecting 
                  eco-conscious consumers with local organic restaurants...
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Powerful AI-Driven Features</h2>
            <p className="section-subtitle">
              Everything you need to transform concepts into fundable ventures
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3 className="feature-title">AI Pitch Refinement</h3>
              <p className="feature-description">
                Transform basic ideas into professional, compelling business pitches 
                using advanced natural language processing.
              </p>
              <div className="feature-list">
                <span>✓ Professional language enhancement</span>
                <span>✓ Market positioning analysis</span>
                <span>✓ Value proposition refinement</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Smart Feasibility Analysis</h3>
              <p className="feature-description">
                Get instant scoring on market potential, technical complexity, 
                and resource requirements with detailed breakdowns.
              </p>
              <div className="feature-list">
                <span>✓ Market potential assessment</span>
                <span>✓ Technical feasibility scoring</span>
                <span>✓ Resource requirement analysis</span>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">💡</div>
              <h3 className="feature-title">Market Insights & Roadmaps</h3>
              <p className="feature-description">
                Receive comprehensive market analysis, risk assessment, 
                and 12-month implementation roadmaps for your ventures.
              </p>
              <div className="feature-list">
                <span>✓ Competitive landscape analysis</span>
                <span>✓ Risk assessment & mitigation</span>
                <span>✓ Implementation planning</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to Build Your Next Big Idea?</h2>
            <p className="cta-subtitle">
              Join entrepreneurs who've transformed their concepts into investor-ready ventures
            </p>
            <button onClick={onGetStarted} className="btn-primary btn-cta">
              <span>Get Started Free</span>
              <span className="btn-icon">→</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
