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

  const replacementAlgos = [
    { value: "fifo", label: "FIFO" },
    { value: "lru", label: "LRU" },
    { value: "optimal", label: "Optimal" },
    { value: "lfu", label: "LFU" },
    { value: "mru", label: "MRU" },
    { value: "mfu", label: "MFU" }
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
    
    try {
      if (!validateRequests(formData.requests)) {
        throw new Error('Please enter valid comma-separated numbers for page requests');
      }

      // Convert requests string to array of numbers
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

  const formatKey = (key) => {
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
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
          <div className="results-grid">
            {results.map((result, index) => (
              <div key={index} className="result-card">
                <h3>{result.paging_type} Paging - {result.algorithm}</h3>
                <div className="result-stats">
                  <div className="stat">
                    <span className="stat-label">Total Page Faults:</span>
                    <span className="stat-value">{result.total_page_faults}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Total Hits:</span>
                    <span className="stat-value">{result.total_hits}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Total Requests:</span>
                    <span className="stat-value">
                      {result.total_page_faults + result.total_hits}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Fault Ratio:</span>
                    <span className="stat-value">
                      {(result.total_page_faults / (result.total_page_faults + result.total_hits)).toFixed(2)}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Hit Ratio:</span>
                    <span className="stat-value">
                      {(result.total_hits / (result.total_page_faults + result.total_hits)).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          !error && <div className="no-results">No results yet. Run a simulation to see the output.</div>
        )}
      </div>
    </div>
  );
};

export default PageReplacementSimulation;
