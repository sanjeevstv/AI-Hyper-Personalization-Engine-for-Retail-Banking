import { useEffect, useState, useCallback } from "react";
import { getLifeEvents } from "../api/client";

const EVENT_COLORS = {
  Promotion: "bg-green-100 text-green-800 border-green-200",
  "Frequent Traveler": "bg-blue-100 text-blue-800 border-blue-200",
  "New Parent": "bg-pink-100 text-pink-800 border-pink-200",
  "Potential Home Buyer": "bg-amber-100 text-amber-800 border-amber-200",
  "Investment Oriented": "bg-purple-100 text-purple-800 border-purple-200",
  "High Spender": "bg-red-100 text-red-800 border-red-200",
  "Credit Disciplined": "bg-teal-100 text-teal-800 border-teal-200",
};

const MODES = [
  { key: "rule", label: "Rule-Based" },
  { key: "ai", label: "AI-Powered" },
];

export default function LifeEvents({ customerId }) {
  const [events, setEvents] = useState([]);
  const [detectionType, setDetectionType] = useState("rule-based");
  const [mode, setMode] = useState("rule");
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState("");

  const fetchEvents = useCallback(
    (m) => {
      setLoading(true);
      setNote("");
      getLifeEvents(customerId, m)
        .then((res) => {
          const data = res.data;
          setEvents(data.events || []);
          setDetectionType(data.detection_type || "rule-based");
          if (data.note) setNote(data.note);
        })
        .catch(() => {
          setEvents([]);
          setDetectionType("rule-based");
        })
        .finally(() => setLoading(false));
    },
    [customerId]
  );

  useEffect(() => {
    fetchEvents(mode);
  }, [customerId, mode, fetchEvents]);

  const isAI = detectionType === "ai";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-gray-800">
            Life Events Detected
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
        <p className="text-sm text-gray-400">Loading...</p>
      ) : events.length === 0 ? (
        <p className="text-sm text-gray-400 italic">
          No life events detected for this customer.
        </p>
      ) : (
        <div className="space-y-3">
          {events.map((event, idx) => {
            const colorClass = isAI
              ? "bg-green-50 text-green-800 border-green-200"
              : EVENT_COLORS[event.event_type] ||
                "bg-gray-100 text-gray-800 border-gray-200";
            return (
              <div
                key={event.id || idx}
                className={`p-3 rounded-lg border ${colorClass}`}
              >
                <div className="font-semibold text-sm">{event.event_type}</div>
                <div className="text-xs mt-1 opacity-80">
                  {event.description}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
