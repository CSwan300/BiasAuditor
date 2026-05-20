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

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'copy';
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (!droppedFile) return;

    const name = droppedFile.name.toLowerCase();
    if (name.endsWith('.csv') || name.endsWith('.xlsx') || name.endsWith('.xls')) {
      setFile(droppedFile);
    } else {
      alert('Unsupported file type. Please use CSV or Excel.');
    }

    e.dataTransfer.clearData();
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    setFile(selectedFile);
  };

  return (
    <div className="config-grid">
      <div className="config-col">
        <div
          className={`drop-zone ${file ? 'active' : ''} ${isDragging ? 'drag-over' : ''}`}
          onClick={handleFileClick}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="drop-icon" style={{ pointerEvents: 'none' }}>
            {file ? '✅' : '📂'}
          </div>
          <p style={{ pointerEvents: 'none' }}>
            {file ? file.name : 'Drop dataset here or browse'}
          </p>
          <input
            type="file"
            ref={fileInputRef}
            hidden
            accept=".csv,.xlsx,.xls"
            onChange={handleInputChange}
          />
        </div>
      </div>

      <div className="config-col">
        <div className="field-group">
          <label className="field-label">
            Fairness Threshold — <span className="accent">{threshold}%</span>
          </label>
          <input
            type="range"
            min="50"
            max="99"
            value={threshold}
            className="slider"
            onChange={(e) => setThreshold(parseInt(e.target.value))}
          />
        </div>

        <div className="field-group">
          <label className="field-label">Outcome Column</label>
          <input
            type="text"
            className="text-input"
            placeholder="e.g. prediction"
            value={outcomeCol}
            onChange={(e) => setOutcomeCol(e.target.value)}
          />
        </div>

        <button
          className="btn-primary"
          onClick={() => file && onRun(file, threshold / 100, outcomeCol)}
          disabled={!file || loading}
        >
          {loading ? 'Analyzing...' : '▶ Run Audit'}
        </button>
      </div>
    </div>
  );
};