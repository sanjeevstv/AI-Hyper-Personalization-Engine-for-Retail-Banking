import { useState } from "react";
import { generateMessage } from "../api/client";

const MESSAGE_TYPES = [
  { key: "email", label: "Email" },
  { key: "push_notification", label: "Push Notification" },
  { key: "rm_talking_points", label: "RM Talking Points" },
  { key: "chatbot", label: "Chatbot" },
];

export default function Messaging({ customerId }) {
  const [messageType, setMessageType] = useState("email");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await generateMessage(customerId, messageType);
      setResult(res.data);
    } catch (err) {
      setResult({
        generated_message:
          err.response?.data?.error || "Failed to generate message",
        model_used: "error",
      });
    }
    setLoading(false);
  };

  const handleCopy = () => {
    if (result?.generated_message) {
      navigator.clipboard.writeText(result.generated_message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4">
        GenAI Personalized Messaging
      </h3>

      <div className="flex flex-wrap gap-2 mb-4">
        {MESSAGE_TYPES.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setMessageType(t.key);
              setResult(null);
            }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              messageType === t.key
                ? "bg-bank-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="px-5 py-2.5 bg-gradient-to-r from-bank-600 to-bank-700 hover:from-bank-700 hover:to-bank-800 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold rounded-lg transition-all text-sm"
      >
        {loading ? "Generating..." : "Generate Message"}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500">
              Model: {result.model_used}
            </span>
            <button
              onClick={handleCopy}
              className="text-xs text-bank-600 hover:text-bank-700 font-medium"
            >
              {copied ? "Copied!" : "Copy to clipboard"}
            </button>
          </div>
          {result.note && (
            <div className="text-xs text-amber-600 mb-2 italic">
              {result.note}
            </div>
          )}
          <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {result.generated_message}
          </div>
        </div>
      )}
    </div>
  );
}
