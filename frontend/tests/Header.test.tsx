import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { Header } from '../src/components/Misc/Header';
import '@testing-library/jest-dom/vitest';
import '@testing-library/jest-dom';

describe('Header', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('renders branding and theme toggle', () => {
    render(<Header />);

    expect(screen.getByText(/Bias/i)).toBeInTheDocument();
    expect(screen.getByText(/Auditor/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
  });

  it('sets dark theme by default', () => {
    render(<Header />);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(localStorage.getItem('bias-auditor-theme')).toBe('dark');
  });

  it('toggles theme and persists it', () => {
    render(<Header />);

    fireEvent.click(screen.getByRole('button', { name: /switch to light mode/i }));

    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(localStorage.getItem('bias-auditor-theme')).toBe('light');
  });
});