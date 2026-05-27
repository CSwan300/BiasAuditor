import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuditConfig } from '../src/components/Audit/AuditConfig';

describe('AuditConfig', () => {
  const onRun = vi.fn();

  beforeEach(() => {
    onRun.mockClear();
  });

  it('disables Run Audit until a file is selected', () => {
    render(<AuditConfig onRun={onRun} loading={false} />);
    expect(screen.getByRole('button', { name: /run audit/i })).toBeDisabled();
  });

  it('allows selecting a valid file through the file input', () => {
    render(<AuditConfig onRun={onRun} loading={false} />);

    // Target the hidden file input
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['a,b\n1,2'], 'data.csv', { type: 'text/csv' });

    // Manually define the files property so the component picks it up
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });

    fireEvent.change(input);

    expect(screen.getByText('data.csv')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /run audit/i })).not.toBeDisabled();
  });

  it('calls onRun with threshold converted to decimal', () => {
    render(<AuditConfig onRun={onRun} loading={false} />);

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['a,b\n1,2'], 'data.csv', { type: 'text/csv' });

    Object.defineProperty(fileInput, 'files', { value: [file], writable: true });
    fireEvent.change(fileInput);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '80' } });

    const outcomeInput = screen.getByPlaceholderText(/e\.g\. prediction/i);
    fireEvent.change(outcomeInput, { target: { value: 'hired' } });

    fireEvent.click(screen.getByRole('button', { name: /run audit/i }));

    expect(onRun).toHaveBeenCalledWith(file, 0.8, 'hired');
  });
});