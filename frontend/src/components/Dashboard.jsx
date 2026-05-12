import { useState } from "react";
import CustomerFilterView from "./CustomerFilterView";
import SegmentOverview from "./SegmentOverview";

const TABS = [
  { key: "customer", label: "Customer View" },
  { key: "segments", label: "Segment Overview" },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("customer");

  return (
    <div>
      <div className="flex gap-2 mb-6">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-5 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === tab.key
                ? "bg-bank-600 text-white shadow-md"
                : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "segments" ? <SegmentOverview /> : <CustomerFilterView />}
    </div>
  );
}
