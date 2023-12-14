import React from "react";
import ResultsMap from "./ResultsMap";

function ResultsPage({ results }) {
  console.log(results);
  return (
    <div className="results">
      <h1>Results Summary</h1>
      <section>
        <h2>Map</h2>
        <ResultsMap data={results} />
      </section>

      <section>
        <h2>Statistics</h2>
        <p>Cache Hit Percentage: {results.cache_hit_percentage}%</p>
        <p>Total Requests: {results.total_requests}</p>
        <p>Average Request Wait Time: {results.average_request_wait_time} ms</p>
        <p>Total Wait Time: {results.total_wait_time} ms</p>
        <p>Minimum Wait Time: {results.min_request_wait_time} ms</p>
        <p>Maximum Wait Time: {results.max_wait_time} ms</p>
        <p>Total Time Elapsed: {results.total_time_elapsed} ms</p>
        <p>Max Request Queue Length: {results.max_queue_length}</p>
      </section>

      <section>
        <h2>Server Log</h2>
        <div className="scroll-box">
          {results.requests[0].map((request, index) => (
            <pre key={index}>{request}</pre>
          ))}
        </div>
      </section>
    </div>
  );
}

export default ResultsPage;
