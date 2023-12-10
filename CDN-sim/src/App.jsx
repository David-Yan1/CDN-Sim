import "./App.css";
import { useState } from "react";
import CDNSimulatorForm from "./CDNSimulatorForm";
import ResultsPage from "./ResultsPage";

function App() {
  let [showResults, setShowResults] = useState(false);
  let [results, setResults] = useState({});
  return (
    <>
      {showResults ? (
        <ResultsPage results={results} />
      ) : (
        <CDNSimulatorForm
          setShowResults={setShowResults}
          setResults={setResults}
        />
      )}
    </>
  );
}

export default App;
