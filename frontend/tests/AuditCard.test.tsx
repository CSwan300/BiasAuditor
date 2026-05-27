import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AuditCard from '../src/components/Audit/AuditCard';

describe('AuditCard', () => {
  it('renders audit details and flagged state', () => {
    render(
      <AuditCard
        index={0}
        audit={{
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
        }}
      />
    );

    expect(screen.getByText('GENDER')).toBeInTheDocument();
    expect(screen.getByText(/Flagged/i)).toBeInTheDocument();

    // DIR Ratio check
    expect(screen.getByText(/0\.500/i)).toBeInTheDocument();

    // 40.0% appears twice: once in the Female group row, once in "Max Gap"
    const percentElements = screen.getAllByText(/40\.0%/i);
    expect(percentElements.length).toBeGreaterThanOrEqual(2);

    expect(screen.getByText('Male')).toBeInTheDocument();
    expect(screen.getByText('Female')).toBeInTheDocument();
  });
});