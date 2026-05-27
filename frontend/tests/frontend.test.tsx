import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

import { App } from '../src/App';
import { Header } from '../src/components/Misc/Header';
import { Footer } from '../src/components/Misc/Footer';
import { Hero } from '../src/components/Misc/Hero';
import RiskBanner from '../src/components/Misc/RiskBanner';
import { AuditConfig } from '../src/components/Audit/AuditConfig';


describe('App', () => {
  it('renders the main layout components', () => {
    render(<App />);

    expect(screen.getByText(/BiasAuditor/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Algorithmic Fairness/i })).toBeInTheDocument();
    expect(screen.getByText(/Open Source Algorithmic Fairness Audit Tool/i)).toBeInTheDocument();
  });
});

describe('Header', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('renders the brand and theme toggle', () => {
    render(<Header />);

    expect(screen.getByText(/Bias/i)).toBeInTheDocument();
    expect(screen.getByText(/Auditor/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
  });

  it('persists theme changes to localStorage and document theme attribute', () => {
    render(<Header />);

    fireEvent.click(screen.getByRole('button', { name: /switch to light mode/i }));

    expect(localStorage.getItem('bias-auditor-theme')).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });
});

describe('Footer', () => {
  it('renders footer text', () => {
    render(<Footer />);
    expect(screen.getByText(/Open Source Algorithmic Fairness Audit Tool/i)).toBeInTheDocument();
  });
});

describe('Hero', () => {
  it('renders hero headline and pills', () => {
    render(<Hero />);

    expect(screen.getByRole('heading', { name: /Algorithmic Fairness/i })).toBeInTheDocument();
    expect(screen.getByText(/Intelligence Platform/i)).toBeInTheDocument();
    expect(screen.getByText(/Intersectionality/i)).toBeInTheDocument();

    const statElements = screen.getAllByText(/Statistical Significance/i);
    expect(statElements.length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText(/Equalized Odds/i)).toBeInTheDocument();
    expect(screen.getByText(/PDF Reports/i)).toBeInTheDocument();
  });
});

describe('RiskBanner', () => {
  it('shows risk level and metadata', () => {
    render(
      <RiskBanner
        risk={{ level: 'High', score: 90, flagged_characteristics: ['gender', 'race'] }}
        meta={{ total_rows: 1000, prediction_column: 'hired' }}
      />
    );

    expect(screen.getByText(/High Risk/i)).toBeInTheDocument();
    expect(screen.getByText(/1,000/i)).toBeInTheDocument();
    expect(screen.getByText(/hired/i)).toBeInTheDocument();
  });

  it('falls back to a default message when no flags exist', () => {
    render(
      <RiskBanner
        risk={{ level: 'Low', score: 10, flagged_characteristics: [] }}
        meta={{ total_rows: 25, prediction_column: 'outcome' }}
      />
    );

    expect(screen.getByText(/Audit complete/i)).toBeInTheDocument();
  });
});

describe('AuditConfig', () => {
  const onRun = vi.fn();

  beforeEach(() => {
    onRun.mockClear();
  });

  it('disables run button until a file is selected', () => {
    render(<AuditConfig onRun={onRun} loading={false} />);
    expect(screen.getByRole('button', { name: /run audit/i })).toBeDisabled();
  });

  it('accepts a valid csv file and enables run button', () => {
    render(<AuditConfig onRun={onRun} loading={false} />);

    const file = new File(['a,b\n1,2'], 'data.csv', { type: 'text/csv' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });

    fireEvent.change(input);

    expect(screen.getByText('data.csv')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /run audit/i })).not.toBeDisabled();
  });
});