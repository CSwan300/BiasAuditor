import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { App } from '../src/App';
import '@testing-library/jest-dom';


describe('App', () => {
  it('renders the main app shell', () => {
    render(<App />);

    expect(screen.getByText(/BiasAuditor/i)).toBeInTheDocument();
    expect(screen.getByText(/Algorithmic Fairness/i)).toBeInTheDocument();
    expect(screen.getByText(/Open Source Algorithmic Fairness Audit Tool/i)).toBeInTheDocument();
  });
});