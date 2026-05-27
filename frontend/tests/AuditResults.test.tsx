import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AuditResults } from '../src/components/Audit/AuditResults';
import { AuditResponse, AuditResult, Mitigation } from '../src/types';

// Mock Browser APIs for PDF generation
vi.stubGlobal('URL', {
  createObjectURL: vi.fn(() => 'blob:mock-url'),
  revokeObjectURL: vi.fn(),
});

// Mock anchor click behavior for downloads
HTMLAnchorElement.prototype.click = vi.fn();

describe('AuditResults', () => {
  const mockReset = vi.fn();
  const mockFile = new File([''], 'test.csv', { type: 'text/csv' });

  const mockAuditData: AuditResponse = {
    overall_risk: {
      level: 'Low',
      score: 10,
      flagged_characteristics: []
    },
    metadata: {
      timestamp: new Date().toISOString(),
      total_rows: 100,
      total_columns: 10,
      prediction_column: 'outcome',
      protected_characteristics_found: ['GENDER'],
      columns_detected: ['GENDER', 'AGE', 'outcome']
    },
    audits: [
      {
        characteristic: 'GENDER',
        groups: [],
        disparity: {
            flag: false,
            disparate_impact_ratio: 1.0,
            max_disparity: 0,
            highest_group: 'N/A',
            lowest_group: 'N/A'
        }
      }
    ],
    mitigations: [
      {
        title: 'Reduce Bias',
        description: 'Test',
        priority: 'medium',
        type: 'preprocessing'
      }
    ],
    warnings: []
  };

  it('downloads a PDF when the backend responds successfully', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(new Blob(['pdf-content'], { type: 'application/pdf' })),
    });
    vi.stubGlobal('fetch', mockFetch);

    render(
      <AuditResults
        data={mockAuditData}
        onReset={mockReset}
        originalFile={mockFile}
        threshold={0.8}
      />
    );

    const downloadBtn = screen.getByRole('button', { name: /download pdf report/i });
    fireEvent.click(downloadBtn);

    expect(mockFetch).toHaveBeenCalled();
  });

  it('calls reset when New Audit is clicked', () => {
    render(
      <AuditResults
        data={mockAuditData}
        onReset={mockReset}
        originalFile={mockFile}
        threshold={0.8}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /new audit/i }));
    expect(mockReset).toHaveBeenCalled();
  });

  it('alerts the user if the source file is missing during download', () => {
    window.alert = vi.fn();

    render(
      <AuditResults
        data={mockAuditData}
        onReset={mockReset}
        originalFile={null} // Simulate missing file
        threshold={0.8}
      />
    );

    const downloadBtn = screen.getByRole('button', { name: /download pdf report/i });
    fireEvent.click(downloadBtn);

    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining("Source file missing"));
  });
});