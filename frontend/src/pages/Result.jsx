import { useLocation, useNavigate } from "react-router-dom";
import ResultCard from "../components/ResultCard";

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();

  const result = location.state?.result;

  if (!result) {
    return (
      <div className="text-center mt-10">
        <h2>No Result</h2>
        <button onClick={() => navigate("/diagnose")}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-10 px-4">
      <ResultCard result={result} />
    </div>
  );
}
