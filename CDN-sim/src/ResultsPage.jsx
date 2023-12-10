import React from "react";
import ResultsMap from "./ResultsMap";

function ResultsPage({ results }) {
  console.log(results);
  return (
    <div className="results">
      <h1>Results Summary</h1>
      <section>
        <h2>Requests Map</h2>
        <ResultsMap data={results}/>
      </section>

      <section>
        <h2>Statistics</h2>
        <p>Cache Hit Percentage: {results.cache_hit_percentage}%</p>
        <p>Total Requests: {results.total_requests}</p>
        <p>Average Request Wait Time: {results.average_request_wait_time}ms</p>
        <p>Total Time: {results.total_time}s</p>
      </section>
    </div>
  );
}

export default ResultsPage;
