import { useState, useEffect } from "react";
import {
  getFilterOptions,
  getFilteredCustomers,
  getCustomer,
} from "../api/client";
import CustomerProfile from "./CustomerProfile";
import LifeEvents from "./LifeEvents";
import Recommendations from "./Recommendations";
import Messaging from "./Messaging";

export default function CustomerFilterView() {
  const [options, setOptions] = useState({
    cities: [],
    occupations: [],
    segments: [],
  });
  const [filters, setFilters] = useState({
    customer_id: "",
    segment: "",
    city: "",
    occupation: "",
    date_from: "",
    date_to: "",
    age_min: "",
    age_max: "",
  });
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [expandedData, setExpandedData] = useState(null);
  const [expandLoading, setExpandLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    getFilterOptions()
      .then((res) => setOptions(res.data))
      .catch(() => {});
  }, []);

  const buildActiveFilters = () => {
    const active = {};
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== "" && v !== null && v !== undefined) active[k] = v;
    });
    return active;
  };

  const handleGo = async () => {
    setLoading(true);
    setSearched(true);
    setExpandedId(null);
    setExpandedData(null);
    try {
      const res = await getFilteredCustomers(buildActiveFilters());
      setCustomers(res.data.customers || []);
      setTotal(res.data.total || 0);
    } catch {
      setCustomers([]);
      setTotal(0);
    }
    setLoading(false);
  };

  const handleExpand = async (customerId) => {
    if (expandedId === customerId) {
      setExpandedId(null);
      setExpandedData(null);
      return;
    }
    setExpandedId(customerId);
    setExpandLoading(true);
    try {
      const res = await getCustomer(customerId);
      setExpandedData(res.data);
    } catch {
      setExpandedData(null);
    }
    setExpandLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleGo();
  };

  const set = (key) => (e) =>
    setFilters((f) => ({ ...f, [key]: e.target.value }));

  const inputCls =
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-bank-500 focus:border-bank-500 outline-none";

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 space-y-3">
        <h3 className="text-sm font-semibold text-gray-700">
          Filter Customers
        </h3>

        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Search by Customer ID
          </label>
          <input
            type="text"
            value={filters.customer_id}
            onChange={set("customer_id")}
            onKeyDown={handleKeyDown}
            placeholder="e.g. CUST_0001"
            className={inputCls}
          />
        </div>

        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-gray-500 mb-1">Segment</label>
            <select
              value={filters.segment}
              onChange={set("segment")}
              onKeyDown={handleKeyDown}
              className={inputCls}
            >
              <option value="">All Segments</option>
              {options.segments.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-gray-500 mb-1">City</label>
            <select
              value={filters.city}
              onChange={set("city")}
              onKeyDown={handleKeyDown}
              className={inputCls}
            >
              <option value="">All Cities</option>
              {options.cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-gray-500 mb-1">
              Occupation
            </label>
            <select
              value={filters.occupation}
              onChange={set("occupation")}
              onKeyDown={handleKeyDown}
              className={inputCls}
            >
              <option value="">All Occupations</option>
              {options.occupations.map((o) => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-gray-500 mb-1">
              Transaction Date From
            </label>
            <input
              type="date"
              value={filters.date_from}
              onChange={set("date_from")}
              onKeyDown={handleKeyDown}
              className={inputCls}
            />
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-gray-500 mb-1">
              Transaction Date To
            </label>
            <input
              type="date"
              value={filters.date_to}
              onChange={set("date_to")}
              onKeyDown={handleKeyDown}
              className={inputCls}
            />
          </div>
          <div className="flex-1 min-w-[100px]">
            <label className="block text-xs text-gray-500 mb-1">
              Min Age
            </label>
            <input
              type="number"
              min="0"
              max="120"
              value={filters.age_min}
              onChange={set("age_min")}
              onKeyDown={handleKeyDown}
              placeholder="e.g. 22"
              className={inputCls}
            />
          </div>
          <div className="flex-1 min-w-[100px]">
            <label className="block text-xs text-gray-500 mb-1">
              Max Age
            </label>
            <input
              type="number"
              min="0"
              max="120"
              value={filters.age_max}
              onChange={set("age_max")}
              onKeyDown={handleKeyDown}
              placeholder="e.g. 45"
              className={inputCls}
            />
          </div>
          <button
            onClick={handleGo}
            disabled={loading}
            className="px-6 py-2 bg-bank-600 hover:bg-bank-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors text-sm"
          >
            {loading ? "Loading..." : "Go"}
          </button>
        </div>
      </div>

      {searched && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-semibold text-gray-700">
              Results: {total} customer{total !== 1 ? "s" : ""}
            </span>
          </div>

          {loading ? (
            <div className="p-4">
              <p className="text-sm text-gray-400">Searching...</p>
            </div>
          ) : customers.length === 0 ? (
            <div className="p-4">
              <p className="text-sm text-gray-400 italic">
                No customers match the selected filters.
              </p>
            </div>
          ) : (
            <div>
              {customers.map((c) => {
                const isExpanded = expandedId === c.customer_id;
                return (
                  <div
                    key={c.customer_id}
                    className="border-b border-gray-100 last:border-0"
                  >
                    <button
                      onClick={() => handleExpand(c.customer_id)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors flex items-center justify-between"
                    >
                      <div className="flex items-center gap-4">
                        <span className="font-medium text-bank-700 w-24">
                          {c.customer_id}
                        </span>
                        <span className="text-sm text-gray-600">
                          {c.occupation}
                        </span>
                        <span className="text-sm text-gray-500">{c.city}</span>
                        <span className="text-sm text-gray-500">
                          Age {c.age}
                        </span>
                        <span className="text-sm text-gray-500">
                          ${c.annual_income?.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {c.segment_name && (
                          <span className="px-2 py-0.5 bg-bank-50 text-bank-700 rounded-full text-xs">
                            {c.segment_name}
                          </span>
                        )}
                        <span
                          className={`text-gray-400 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                        >
                          &#9660;
                        </span>
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="px-4 pb-4 bg-gray-50/50">
                        {expandLoading ? (
                          <p className="text-sm text-gray-400 py-4">
                            Loading details...
                          </p>
                        ) : expandedData ? (
                          <div className="space-y-4 pt-2">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                              <CustomerProfile customer={expandedData} />
                              <LifeEvents customerId={c.customer_id} />
                            </div>
                            <Recommendations customerId={c.customer_id} />
                            <Messaging customerId={c.customer_id} />
                          </div>
                        ) : (
                          <p className="text-sm text-red-400 py-4">
                            Failed to load customer details.
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
