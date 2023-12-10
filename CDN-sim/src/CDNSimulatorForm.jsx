import { useState } from "react";
import Map from "./Map";
import MultiMap from "./MultiMap";

function CDNSimulatorForm({ setShowResults, setResults }) {
  const [coordinates, setCoordinates] = useState([0, 0]);
  const [nodeCoordinates, setNodeCoordinates] = useState([]);
  const [numberOfUsers, setNumberOfUsers] = useState(50);
  const [cachePolicy, setCachePolicy] = useState(0);
  const [cacheSize, setCacheSize] = useState(50);
  const [latency, setLatency] = useState(50);
  const [rerouteRequests, setRerouteRequests] = useState(false);
  const [maxConcurrentRequests, setMaxConcurrentRequests] = useState(50);

  const API_HOST = "http://127.0.0.1:5000";

  const runSimulation = async (queryString) => {
    return fetch(`${API_HOST}/simulate?${queryString}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.text();
      })
      .then((data) => {
        console.log("Success:", data);
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = {
      numberOfUsers,
      cachePolicy,
      cacheSize,
      latency,
      rerouteRequests,
      maxConcurrentRequests,
      coordinates,
      nodeCoordinates,
    };
    const queryString = new URLSearchParams({
      data: JSON.stringify(formData),
    }).toString();
    const data = await runSimulation(queryString);
    const results = JSON.parse(data);
    setResults(results["data"]);
    setShowResults(true);
  };
  const handleReset = () => {
    setNodeCoordinates([]);
  };
  return (
    <form onSubmit={handleSubmit} className="cdn-form">
      <h1>CDN Simulator</h1>
      <em>Made by David Yan and Everett Shen</em>

      <h2>Initializing Server and Users</h2>
      {/* Origin server location */}
      <div>
        <label>Where do you want the origin server to be?</label>
        <Map coordinates={coordinates} setCoordinates={setCoordinates} />
      </div>
      {/* Node server locations */}
      <div>
        <label>Where do you want the node servers to be?</label>
        <MultiMap
          coordinates={nodeCoordinates}
          setCoordinates={setNodeCoordinates}
        />
        <button type="button" onClick={handleReset}>
          Reset
        </button>
      </div>
      {/* Number of Users */}
      <div>
        <label>How many users do you want?</label>
        <input
          type="range"
          min="1"
          max="100"
          value={numberOfUsers}
          onChange={(e) => setNumberOfUsers(e.target.value)}
        />
        <span>{numberOfUsers}</span>
      </div>

      <h2>Caching Details</h2>
      {/* Cache Eviction Policy */}
      <div>
        <label>Cache eviction policy:</label>
        <select
          value={cachePolicy}
          onChange={(e) => setCachePolicy(e.target.value)}
        >
          <option value={0}>LRU</option>
          <option value={1}>FIFO</option>
          <option value={2}>LFU</option>
        </select>
      </div>
      {/* Cache Size */}
      <div>
        <label>Cache size:</label>
        <input
          type="range"
          min="1"
          max="100"
          value={cacheSize}
          onChange={(e) => setCacheSize(e.target.value)}
        />
        <span>{cacheSize}</span>
      </div>

      <h2>Additional Inputs</h2>
      {/* Latency */}
      <div>
        <label>Latency (ms):</label>
        <input
          type="range"
          min="1"
          max="100"
          value={latency}
          onChange={(e) => setLatency(e.target.value)}
        />
        <span>{latency}</span>
      </div>

      {/* Max Concurrent Requests Per Server */}
      <div>
        <label>Max concurrent requests per server:</label>
        <input
          type="range"
          min="10"
          max="100"
          value={maxConcurrentRequests}
          onChange={(e) => setMaxConcurrentRequests(e.target.value)}
        />
        <span>{maxConcurrentRequests}</span>
      </div>
      {/* Reroute Requests */}
      <div>
        <label>
          <input
            type="checkbox"
            checked={rerouteRequests}
            onChange={(e) => setRerouteRequests(e.target.checked)}
          />
          Reroute requests away from congested servers?
        </label>
      </div>
      <button
        type="submit"
        style={{ backgroundColor: "#ADD8E6", marginTop: 50 }}
      >
        Start simulation
      </button>
    </form>
  );
}

export default CDNSimulatorForm;
