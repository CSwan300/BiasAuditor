import React, { useRef, useState } from 'react';

interface Props {
  onRun: (file: File, threshold: number, outcome: string) => void;
  loading: boolean;
}

export const AuditConfig: React.FC<Props> = ({ onRun, loading }) => {
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState(80);
  const [outcomeCol, setOutcomeCol] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="config-grid">
      <div className="config-col">
        <div
          className={`drop-zone ${file ? 'active' : ''} ${isDragging ? 'drag-over' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <div className="drop-icon">{file ? '✅' : '📂'}</div>
          <p>{file ? file.name : "Drop dataset here or browse"}</p>
          <input type="file" ref={fileInputRef} hidden accept=".csv,.xlsx,.xls"
                 onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </div>
      </div>

      <div className="config-col">
        <div className="field-group">
          <label className="field-label">Fairness Threshold — <span className="accent">{threshold}%</span></label>
          <input type="range" min="50" max="99" value={threshold} className="slider"
                 onChange={(e) => setThreshold(parseInt(e.target.value))} />
        </div>
        <div className="field-group">
          <label className="field-label">Outcome Column</label>
          <input type="text" className="text-input" placeholder="e.g. prediction"
                 value={outcomeCol} onChange={(e) => setOutcomeCol(e.target.value)} />
        </div>
        <button className="btn-primary" onClick={() => file && onRun(file, threshold, outcomeCol)}
                disabled={!file || loading}>
          {loading ? 'Analyzing...' : '▶ Run Audit'}
        </button>
      </div>
    </div>
  );
};