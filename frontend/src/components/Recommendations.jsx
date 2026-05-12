import { useEffect, useState, useCallback } from "react";
import { getRecommendations } from "../api/client";

const MODES = [
  { key: "rule", label: "Rule-Based" },
  { key: "ai", label: "AI-Powered" },
];

export default function Recommendations({ customerId }) {
  const [recs, setRecs] = useState([]);
  const [reasoningType, setReasoningType] = useState("rule-based");
  const [mode, setMode] = useState("rule");
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState("");

  const fetchRecs = useCallback(
    (m) => {
      setLoading(true);
      setNote("");
      getRecommendations(customerId, m)
        .then((res) => {
          const data = res.data;
          setRecs(data.recommendations || []);
          setReasoningType(data.reasoning_type || "rule-based");
          if (data.note) setNote(data.note);
        })
        .catch(() => {
          setRecs([]);
          setReasoningType("rule-based");
        })
        .finally(() => setLoading(false));
    },
    [customerId]
  );

  useEffect(() => {
    fetchRecs(mode);
  }, [customerId, mode, fetchRecs]);

  const isAI = reasoningType === "ai";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-gray-800">
            Product Recommendations
          </h3>
          <span
            className={`px-3 py-1 text-xs font-semibold rounded-full ${
              isAI
                ? "bg-green-100 text-green-700 border border-green-300"
                : "bg-gray-100 text-gray-600 border border-gray-300"
            }`}
          >
            {isAI ? "AI-Powered" : "Rule-Based"}
          </span>
        </div>
        <div className="flex gap-1">
          {MODES.map((m) => (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                mode === m.key
                  ? m.key === "ai"
                    ? "bg-green-600 text-white"
                    : "bg-gray-700 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {note && (
        <div className="mb-3 text-xs text-amber-600 italic">{note}</div>
      )}

      {loading ? (
        <p className="text-sm text-gray-400">Loading recommendations...</p>
      ) : recs.length === 0 ? (
        <p className="text-sm text-gray-400 italic">
          No recommendations available.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recs.map((rec, idx) => (
            <div
              key={rec.product.product_id}
              className={`border rounded-xl p-4 hover:shadow-md transition-shadow ${
                isAI ? "border-green-200 bg-green-50/30" : "border-gray-200"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                    isAI
                      ? "bg-green-100 text-green-700"
                      : "bg-bank-100 text-bank-700"
                  }`}
                >
                  #{idx + 1}
                </span>
                <span className="text-xs text-gray-500 uppercase tracking-wider">
                  {rec.product.product_type}
                </span>
              </div>
              <h4 className="font-semibold text-gray-800 mb-1">
                {rec.product.product_name}
              </h4>
              <p className="text-xs text-gray-500 mb-3">
                {rec.product.benefits}
              </p>

              <div className="border-t border-gray-100 pt-2">
                <div className="text-xs font-semibold text-gray-600 mb-1">
                  {isAI ? "AI Reasoning:" : "Rule-Based Reasoning:"}
                </div>
                {isAI ? (
                  <p className="text-xs text-gray-600 leading-relaxed">
                    {rec.reasons[0]}
                  </p>
                ) : (
                  <ul className="space-y-0.5">
                    {rec.reasons.map((r, i) => (
                      <li
                        key={i}
                        className="text-xs text-gray-500 flex gap-1"
                      >
                        <span className="text-bank-500 mt-0.5">&bull;</span>
                        {r}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {!isAI && rec.score > 0 && (
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-gray-400">
                    Score: {rec.score}
                  </span>
                  <span className="text-xs text-gray-400">
                    Min Income: $
                    {rec.product.eligibility_income?.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
