import { render, screen } from '@testing-library/react';
import { Hero } from '../src/components/Misc/Hero';
import { describe, expect, it } from 'vitest';

describe('Hero', () => {
  it('renders the main heading', () => {
    render(<Hero />);
    expect(screen.getByText('Algorithmic Fairness')).toBeInTheDocument();
  });

  it('renders the accent span text', () => {
    render(<Hero />);
    expect(screen.getByText('Intelligence Platform')).toBeTruthy();
  });

  it('renders the subtitle text', () => {
    render(<Hero />);
    expect(screen.getByText(/Detect, measure, and mitigate bias/i)).toBeInTheDocument();
  });

  it('renders the Four-Fifths Rule reference', () => {
    render(<Hero />);
    expect(screen.getByText(/Four-Fifths Rule/i)).toBeInTheDocument();
  });

  it('renders all feature pills', () => {
    render(<Hero />);
    expect(screen.getByText('Intersectionality')).toBeInTheDocument();
    expect(screen.getByText('Statistical Significance')).toBeInTheDocument();
    expect(screen.getByText('Equalized Odds')).toBeInTheDocument();
    expect(screen.getByText('PDF Reports')).toBeInTheDocument();
  });

  it('renders exactly four pills', () => {
    const { container } = render(<Hero />);
    const pills = container.querySelectorAll('.pill');
    expect(pills).toHaveLength(4);
  });

  it('renders inside a section element', () => {
    const { container } = render(<Hero />);
    expect(container.querySelector('section.hero')).toBeInTheDocument();
  });
});