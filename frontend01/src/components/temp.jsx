import React, { useState } from "react";
import "../styles/MemorySimulation.css";

const MemorySimulation = () => {
  const [formData, setFormData] = useState({
    total_virtual_pages: 100,
    total_physical_frames: 10,
    page_size: 4096,
    page_table_type: "single",
    tlb_size: 5,
    replacement_algo: "fifo",
    total_access_requests: 1000,
    memory_requests: ""
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useCustomRequests, setUseCustomRequests] = useState(false);

  const pageTableTypes = [
    { value: "single", label: "Single Level" },
    { value: "multi", label: "Multi Level" },
    { value: "inverted", label: "Inverted" },
    { value: "all", label: "All" }
  ];

  const replacementAlgos = [
    { value: "fifo", label: "FIFO" },
    { value: "lru", label: "LRU" },
    { value: "lfu", label: "LFU" },
    { value: "optimal", label: "Optimal" },
    { value: "all", label: "All" }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCheckboxChange = () => {
    setUseCustomRequests(!useCustomRequests);
  };

  const validateMemoryRequests = (input) => {
    if (!input) return false;
    return input.split(',').every(item => !isNaN(parseInt(item.trim())));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      // Validate inputs
      if (useCustomRequests && !validateMemoryRequests(formData.memory_requests)) {
        throw new Error('Please enter valid comma-separated numbers for memory requests');
      }

      // Prepare request data
      const requestData = {
        total_virtual_pages: parseInt(formData.total_virtual_pages),
        total_physical_frames: parseInt(formData.total_physical_frames),
        tlb_size: parseInt(formData.tlb_size),
        page_table_type: formData.page_table_type,
        replacement_algo: formData.replacement_algo,
      };

      // Add either memory_requests or total_access_requests
      if (useCustomRequests) {
        requestData.memory_requests = formData.memory_requests;
      } else {
        requestData.total_access_requests = parseInt(formData.total_access_requests);
      }

      const response = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Network response was not ok');
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

  // Helper function to format display keys
  const formatKey = (key) => {
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="memory-simulation-container">
      <form className="simulation-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="input-group">
            <label htmlFor="total_virtual_pages">Total Virtual Pages</label>
            <input
              type="number"
              id="total_virtual_pages"
              name="total_virtual_pages"
              value={formData.total_virtual_pages}
              onChange={handleInputChange}
              required
              min="1"
            />
          </div>

          <div className="input-group">
            <label htmlFor="total_physical_frames">Total Physical Frames</label>
            <input
              type="number"
              id="total_physical_frames"
              name="total_physical_frames"
              value={formData.total_physical_frames}
              onChange={handleInputChange}
              required
              min="1"
            />
          </div>

          <div className="input-group">
            <label htmlFor="page_size">Page Size (Bytes)</label>
            <input
              type="number"
              id="page_size"
              name="page_size"
              value={formData.page_size}
              onChange={handleInputChange}
              required
              min="1"
            />
          </div>

          <div className="input-group">
            <label htmlFor="page_table_type">Page Table Type</label>
            <select
              id="page_table_type"
              name="page_table_type"
              value={formData.page_table_type}
              onChange={handleInputChange}
            >
              {pageTableTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label htmlFor="tlb_size">TLB Size</label>
            <input
              type="number"
              id="tlb_size"
              name="tlb_size"
              value={formData.tlb_size}
              onChange={handleInputChange}
              required
              min="1"
            />
          </div>

          <div className="input-group">
            <label htmlFor="replacement_algo">Page Replacement Algorithm</label>
            <select
              id="replacement_algo"
              name="replacement_algo"
              value={formData.replacement_algo}
              onChange={handleInputChange}
            >
              {replacementAlgos.map((algo) => (
                <option key={algo.value} value={algo.value}>
                  {algo.label}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={useCustomRequests}
                onChange={handleCheckboxChange}
              />
              Use custom memory requests
            </label>
          </div>

          {useCustomRequests ? (
            <div className="input-group full-width">
              <label htmlFor="memory_requests">Memory Requests (comma-separated)</label>
              <input
                type="text"
                id="memory_requests"
                name="memory_requests"
                value={formData.memory_requests}
                onChange={handleInputChange}
                placeholder="e.g., 1,2,3,4,5,2,3,1,5"
                required={useCustomRequests}
              />
            </div>
          ) : (
            <div className="input-group">
              <label htmlFor="total_access_requests">Total Memory Access Requests</label>
              <input
                type="number"
                id="total_access_requests"
                name="total_access_requests"
                value={formData.total_access_requests}
                onChange={handleInputChange}
                required={!useCustomRequests}
                min="1"
              />
            </div>
          )}
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
                <h3>{result.paging_type} PAGING WITH {result.algorithm}</h3>
                <div className="result-stats">
                  {Object.entries(result).map(([key, value]) => {
                    if (key === 'paging_type' || key === 'algorithm') return null;
                    return (
                      <div className="stat" key={key}>
                        <span className="stat-label">{formatKey(key)}:</span>
                        <span className="stat-value">
                          {typeof value === 'number' ? 
                            Number.isInteger(value) ? value : value.toFixed(2) 
                            : value}
                        </span>
                      </div>
                    );
                  })}
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

export default MemorySimulation;