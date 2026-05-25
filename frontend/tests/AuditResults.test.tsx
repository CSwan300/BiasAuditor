import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuditResults } from '../src/components/Audit/AuditResults';

describe('AuditResults', () => {
  const onReset = vi.fn();
  const originalFile = new File(['a,b\n1,2'], 'dataset.csv', { type: 'text/csv' });

  const data = {
    overall_risk: { level: 'High', score: 90, flagged_characteristics: ['gender'] },
    metadata: {
      total_rows: 100,
      prediction_column: 'hired',
      protected_characteristics_found: ['gender'],
    },
    warnings: [],
    audits: [
      {
        characteristic: 'GENDER',
        groups: [
          { group: 'Male', rate: 80, count: 100, percentage: '80%' },
          { group: 'Female', rate: 40, count: 100, percentage: '40%' },
        ],
        disparity: {
          disparate_impact_ratio: 0.5,
          max_disparity: 40,
          flag: true,
          highest_group: 'Male',
          lowest_group: 'Female',
        },
      },
    ],
    mitigations: [
      {
        type: 'reweighting',
        priority: 'high' as const,
        title: 'Reweight Samples',
        description: 'Adjust sample weights to reduce disparity.',
      },
    ],
  };

  beforeEach(() => {
    onReset.mockClear();
    vi.restoreAllMocks();
  });

  it('renders risk banner, audits, and mitigations', () => {
    render(<AuditResults data={data as any} onReset={onReset} originalFile={originalFile} threshold={0.8} />);

    expect(screen.getByText(/High Risk/i)).toBeInTheDocument();
    expect(screen.getByText(/GENDER/i)).toBeInTheDocument();
    expect(screen.getByText(/Recommended Mitigations/i)).toBeInTheDocument();
    expect(screen.getByText(/Reweight Samples/i)).toBeInTheDocument();
  });

  it('calls reset when New Audit is clicked', () => {
    render(<AuditResults data={data as any} onReset={onReset} originalFile={originalFile} threshold={0.8} />);

    fireEvent.click(screen.getByRole('button', { name: /new audit/i }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it('downloads a PDF when the backend responds successfully', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: vi.fn().mockResolvedValue(new Blob(['pdf'], { type: 'application/pdf' })),
    });

    vi.stubGlobal('fetch', fetchMock);

    render(<AuditResults data={data as any} onReset={onReset} originalFile={originalFile} threshold={0.8} />);

    fireEvent.click(screen.getByRole('button', { name: /download pdf report/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    expect(fetchMock.mock.calls[0][0]).toContain('/report/pdf');
  });

  it('alerts on PDF generation failure', async () => {
    window.alert = vi.fn();

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: vi.fn().mockResolvedValue({ detail: 'PDF generation failed' }),
      })
    );

    render(<AuditResults data={data as any} onReset={onReset} originalFile={originalFile} threshold={0.8} />);

    fireEvent.click(screen.getByRole('button', { name: /download pdf report/i }));

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalled();
    });
  });
});