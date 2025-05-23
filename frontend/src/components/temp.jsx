import React, { useState } from "react";
import "../styles/MemorySimulation.css";

const PageReplacementSimulation = () => {
  const [formData, setFormData] = useState({
    frames: 3,
    algorithm: "fifo",
    requests: "1,2,3,4,1,2,5,1,2,3,4,5"
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState(null);
  const [activeResultIndex, setActiveResultIndex] = useState(0);
  const [showGraphicalComparison, setShowGraphicalComparison] = useState(false);

  const replacementAlgos = [
    { value: "fifo", label: "FIFO" },
    { value: "lru", label: "LRU" },
    { value: "optimal", label: "Optimal" },
    { value: "lfu", label: "LFU" },
    { value: "mru", label: "MRU" },
    { value: "mfu", label: "MFU" },
    { value: "all", label: "Compare All Algorithms" }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateRequests = (input) => {
    if (!input) return false;
    return input.split(',').every(item => !isNaN(parseInt(item.trim())));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setViewMode(null);
    setShowGraphicalComparison(false);
    
    try {
      if (!validateRequests(formData.requests)) {
        throw new Error('Please enter valid comma-separated numbers for page requests');
      }

      const requestsArray = formData.requests.split(',').map(num => parseInt(num.trim()));

      const requestData = {
        requests: requestsArray,
        frames: parseInt(formData.frames),
        algorithm: formData.algorithm
      };

      const response = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
      }
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const renderFinalMemoryState = (result) => {
    return (
      <div className="result-view">
        <h4>Final Memory State:</h4>
        <div className="memory-frames">
          {result.final_memory_state && Array.isArray(result.final_memory_state) ? (
            <table className="memory-table">
              <thead>
                <tr>
                  <th>Frame</th>
                  <th>Page</th>
                </tr>
              </thead>
              <tbody>
                {result.final_memory_state.map((page, idx) => (
                  <tr key={idx}>
                    <td>{idx}</td>
                    <td>{page !== null ? page : "Empty"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="no-memory">No memory state available</div>
          )}
        </div>
      </div>
    );
  };

  const renderPageTable = (result) => {
    return (
      <div className="result-view">
        <h4>Page Table Evolution:</h4>
        <div className="page-table-container">
          {result.page_table && Array.isArray(result.page_table) ? (
            <table className="page-table">
              <thead>
                <tr>
                  <th>Steps</th>
                  {result.page_table.map((_, step) => (
                    <th key={step}>{step + 1}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: formData.frames }).map((_, frameIdx) => (
                  <tr key={frameIdx}>
                    <td className="frame-label">Frame {frameIdx}</td>
                    {result.page_table.map((frameState, step) => (
                      <td key={`${frameIdx}-${step}`}>
                        {frameState[frameIdx] !== null ? frameState[frameIdx] : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="no-page-table">No page table data available</div>
          )}
        </div>
      </div>
    );
  };

  const renderDetails = (result) => {
    return (
      <div className="result-view">
        <h4>Detailed Steps:</h4>
        <div className="details-container">
          {result.history && Array.isArray(result.history) ? (
            <table className="details-table">
              <thead>
                <tr>
                  <th>Step</th>
                  <th>Page</th>
                  <th>Event</th>
                  <th>Action</th>
                  <th>Memory State</th>
                </tr>
              </thead>
              <tbody>
                {result.history.map((entry, idx) => (
                  <tr key={idx} className={entry.event}>
                    <td>{entry.step}</td>
                    <td>{entry.page}</td>
                    <td className={`event-${entry.event}`}>
                      {entry.event.toUpperCase()}
                    </td>
                    <td>{entry.action || "-"}</td>
                    <td>
                      {entry.memory.map((page, i) => (
                        <span key={i} className="memory-page">
                          {page !== null ? page : "-"}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="no-details">No detailed history available</div>
          )}
        </div>
      </div>
    );
  };

const renderGraphicalComparison = () => {
    if (results.length !== 6) return null;

    // Calculate max and min values for coloring
    const hitRatios = results.map(result => 
      result.hit_ratio || (result.total_hits / (result.total_page_faults + result.total_hits))
    );
    const faultRatios = results.map(result => 
      result.fault_ratio || (result.total_page_faults / (result.total_page_faults + result.total_hits))
    );

    const maxHitRatio = Math.max(...hitRatios);
    const minHitRatio = Math.min(...hitRatios);
    const maxFaultRatio = Math.max(...faultRatios);
    const minFaultRatio = Math.min(...faultRatios);

    return (
      <div className="graphical-comparison">
        <h3>Algorithm Performance Comparison</h3>
        
        <div className="comparison-charts">
          <div className="chart-container">
            <h4>Fault Ratio Comparison</h4>
            <div className="vertical-bar-chart">
              <div className="chart-y-axis">
                <span>1.0</span>
                <span>0.8</span>
                <span>0.6</span>
                <span>0.4</span>
                <span>0.2</span>
                <span>0.0</span>
              </div>
              <div className="chart-bars-container">
                {results.map((result, index) => {
                  const faultRatio = result.fault_ratio || 
                    (result.total_page_faults / (result.total_page_faults + result.total_hits));
                  const isWorst = faultRatio === maxFaultRatio;
                  const isBest = faultRatio === minFaultRatio;
                  
                  return (
                    <div key={index} className="bar-vertical-container">
                      <div 
                        className={`bar-vertical ${isWorst ? 'worst' : ''} ${isBest ? 'best' : ''}`}
                        style={{ 
                          height: `${faultRatio * 100}%`,
                          backgroundColor: isWorst ? '#ff6b6b' : isBest ? '#51cf66' : '#339af0'
                        }}
                      >
                        <span className="bar-value">{faultRatio.toFixed(3)}</span>
                      </div>
                      <div className="bar-label">{result.algorithm}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="chart-container">
            <h4>Hit Ratio Comparison</h4>
            <div className="vertical-bar-chart">
              <div className="chart-y-axis">
                <span>1.0</span>
                <span>0.8</span>
                <span>0.6</span>
                <span>0.4</span>
                <span>0.2</span>
                <span>0.0</span>
              </div>
              <div className="chart-bars-container">
                {results.map((result, index) => {
                  const hitRatio = result.hit_ratio || 
                    (result.total_hits / (result.total_page_faults + result.total_hits));
                  const isBest = hitRatio === maxHitRatio;
                  const isWorst = hitRatio === minHitRatio;
                  
                  return (
                    <div key={index} className="bar-vertical-container">
                      <div 
                        className={`bar-vertical ${isBest ? 'best' : ''} ${isWorst ? 'worst' : ''}`}
                        style={{ 
                          height: `${hitRatio * 100}%`,
                          backgroundColor: isBest ? '#51cf66' : isWorst ? '#ff6b6b' : '#339af0'
                        }}
                      >
                        <span className="bar-value">{hitRatio.toFixed(3)}</span>
                      </div>
                      <div className="bar-label">{result.algorithm}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="memory-simulation-container">
      <h1>Page Replacement Algorithm Simulator</h1>
      
      <form className="simulation-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="input-group">
            <label htmlFor="requests">Page Requests (comma-separated)</label>
            <input
              type="text"
              id="requests"
              name="requests"
              value={formData.requests}
              onChange={handleInputChange}
              placeholder="e.g., 1,2,3,4,1,2,5"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="frames">Number of Frames</label>
            <input
              type="number"
              id="frames"
              name="frames"
              value={formData.frames}
              onChange={handleInputChange}
              required
              min="1"
            />
          </div>

          <div className="input-group">
            <label htmlFor="algorithm">Replacement Algorithm</label>
            <select
              id="algorithm"
              name="algorithm"
              value={formData.algorithm}
              onChange={handleInputChange}
            >
              {replacementAlgos.map((algo) => (
                <option key={algo.value} value={algo.value}>
                  {algo.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="button-container">
          <button type="submit" disabled={loading}>
            {loading ? 'Running Simulation...' : 'Run Simulation'}
          </button>
          {results.length === 6 && (
            <button 
              type="button" 
              className="graphical-comparison-btn"
              onClick={() => setShowGraphicalComparison(!showGraphicalComparison)}
            >
              {showGraphicalComparison ? 'Hide Comparison' : 'Graphical Comparison'}
            </button>
          )}
        </div>
      </form>

      <div className="results-container">
        <h2>Simulation Results</h2>
        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}
        {loading ? (
          <div className="loading">Loading results...</div>
        ) : results.length > 0 ? (
          <>
            {showGraphicalComparison && renderGraphicalComparison()}
            
            <div className={`results-grid ${results.length > 1 ? 'multi-results' : ''}`}>
              {results.map((result, index) => (
                <div 
                  key={index} 
                  className={`result-card ${results.length > 1 ? 'compact' : ''} ${activeResultIndex === index ? 'active' : ''}`}
                  onClick={() => setActiveResultIndex(index)}
                >
                  <h3>{result.algorithm}</h3>
                  <div className="result-stats">
                    <div className="stat">
                      <span className="stat-label">Total Requests:</span>
                      <span className="stat-value">
                        {result.total_page_faults + result.total_hits}
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Page Faults:</span>
                      <span className="stat-value">{result.total_page_faults}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Hits:</span>
                      <span className="stat-value">{result.total_hits}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Fault Ratio:</span>
                      <span className="stat-value">
                        {result.fault_ratio ? result.fault_ratio.toFixed(3) : 
                         (result.total_page_faults / (result.total_page_faults + result.total_hits)).toFixed(3)}
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Hit Ratio:</span>
                      <span className="stat-value">
                        {result.hit_ratio ? result.hit_ratio.toFixed(3) : 
                         (result.total_hits / (result.total_page_faults + result.total_hits)).toFixed(3)}
                      </span>
                    </div>
                    <div className="view-controls">
  <button 
    className={viewMode === 'final' ? 'active' : ''}
    onClick={() => setViewMode(viewMode === 'final' ? null : 'final')}
  >
    Final Memory State
  </button>
  <button 
    className={viewMode === 'pageTable' ? 'active' : ''}
    onClick={() => setViewMode(viewMode === 'pageTable' ? null : 'pageTable')}
  >
    Page Table
  </button>
  <button 
    className={viewMode === 'details' ? 'active' : ''}
    onClick={() => setViewMode(viewMode === 'details' ? null : 'details')}
  >
    Details
  </button>
</div>
                  </div>
                </div>
              ))}
            </div>

           

            <div className="result-view-container">
              {viewMode === 'final' && renderFinalMemoryState(results[activeResultIndex])}
              {viewMode === 'pageTable' && renderPageTable(results[activeResultIndex])}
              {viewMode === 'details' && renderDetails(results[activeResultIndex])}
            </div>
          </>
        ) : (
          !error && <div className="no-results">No results yet. Run a simulation to see the output.</div>
        )}
      </div>
    </div>
  );
};

export default PageReplacementSimulation;