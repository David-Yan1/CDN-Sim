import React from "react";

function ResultsPage({ results }) {
  console.log(results);
  return (
    <div className="results">
      <h1>Results Summary</h1>
      {/* TODO: add requests map */}
      <section>
        <h2>Requests</h2>
        <ul>
          {results.requests.map((request, index) => (
            <li key={index}>
              Origin: ({request[0][0]}, {request[0][1]}), Destination: (
              {request[1][0]}, {request[1][1]}), Timestamp: {request[2]}, Cache
              Hit: {request[3] ? "Yes" : "No"}
            </li>
          ))}
        </ul>
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
