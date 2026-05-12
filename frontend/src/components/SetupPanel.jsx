import { useState } from "react";
import {
  seedData,
  computeProfiles,
  detectLifeEvents,
  runSegmentation,
} from "../api/client";

const STEPS = [
  { key: "seed", label: "Load Seed Data", fn: seedData },
  { key: "profiles", label: "Compute Customer Profiles", fn: computeProfiles },
  { key: "events", label: "Detect Life Events", fn: detectLifeEvents },
  { key: "segments", label: "Run Segmentation", fn: runSegmentation },
];

export default function SetupPanel({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(-1);
  const [results, setResults] = useState({});
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);

  const runAll = async () => {
    setRunning(true);
    setError(null);
    for (let i = 0; i < STEPS.length; i++) {
      setCurrentStep(i);
      try {
        const res = await STEPS[i].fn();
        setResults((prev) => ({ ...prev, [STEPS[i].key]: res.data }));
      } catch (err) {
        setError(
          `Failed at "${STEPS[i].label}": ${err.response?.data?.error || err.message}`
        );
        setRunning(false);
        return;
      }
    }
    setCurrentStep(STEPS.length);
    setRunning(false);
  };

  const allDone = currentStep === STEPS.length;

  return (
    <div className="max-w-xl mx-auto mt-12">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          System Initialization
        </h2>
        <p className="text-gray-500 mb-6">
          Load sample data and run the AI pipeline to get started.
        </p>

        <div className="space-y-3 mb-6">
          {STEPS.map((step, idx) => {
            let status = "pending";
            if (idx < currentStep) status = "done";
            else if (idx === currentStep && running) status = "running";

            return (
              <div
                key={step.key}
                className={`flex items-center gap-3 p-3 rounded-lg border ${
                  status === "done"
                    ? "bg-green-50 border-green-200"
                    : status === "running"
                      ? "bg-blue-50 border-blue-200"
                      : "bg-gray-50 border-gray-200"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    status === "done"
                      ? "bg-green-500 text-white"
                      : status === "running"
                        ? "bg-blue-500 text-white animate-pulse"
                        : "bg-gray-300 text-gray-600"
                  }`}
                >
                  {status === "done" ? "\u2713" : idx + 1}
                </div>
                <span
                  className={`font-medium ${status === "done" ? "text-green-700" : status === "running" ? "text-blue-700" : "text-gray-600"}`}
                >
                  {step.label}
                </span>
                {status === "running" && (
                  <span className="ml-auto text-xs text-blue-500">
                    Processing...
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {!allDone ? (
          <button
            onClick={runAll}
            disabled={running}
            className="w-full py-3 bg-bank-600 hover:bg-bank-700 disabled:bg-gray-400 text-white font-semibold rounded-xl transition-colors"
          >
            {running ? "Initializing..." : "Initialize System"}
          </button>
        ) : (
          <button
            onClick={onComplete}
            className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-colors"
          >
            Open Dashboard
          </button>
        )}
      </div>
    </div>
  );
}
