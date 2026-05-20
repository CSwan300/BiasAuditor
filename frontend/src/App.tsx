import Header from './components/Header';
import Footer from './components/Footer';
import { LandingPage } from './pages/LandingPage';

function App() {
  return (
    <div className="app-container">
      <Header />
       {/* In the future, for a Router,
          the <Routes> would go here instead of <LandingPage />
      */}
      <LandingPage />

      <Footer />
    </div>
  );
}

export default App;