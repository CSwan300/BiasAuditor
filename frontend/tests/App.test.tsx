import { render, screen, within } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { App } from '../src/App';

describe('App', () => {
  it('renders the main app shell', () => {
    render(<App />);

    // 1. Target the Header specifically using the 'banner' ARIA role
    // This fixes the "Multiple elements found" error for "Bias"
    const header = screen.getByRole('banner');
    expect(within(header).getByText(/Bias/i)).toBeInTheDocument();
    expect(within(header).getByText(/Auditor/i)).toBeInTheDocument();

    // 2. Target the Hero Heading specifically by its role
    // This distinguishes it from other text in the description or footer
    expect(screen.getByRole('heading', { name: /Algorithmic Fairness/i })).toBeInTheDocument();

    // 3. Verify the unique Footer tagline
    expect(screen.getByText(/Open Source Algorithmic Fairness Audit Tool/i)).toBeInTheDocument();

    // 4. Verify the Audit configuration area is visible
    // This ensures the main functional part of the app is rendered
    expect(screen.getByText(/Drop dataset here/i)).toBeInTheDocument();
  });
});