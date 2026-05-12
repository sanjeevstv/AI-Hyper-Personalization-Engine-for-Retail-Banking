import { useState, useEffect, useRef } from "react";
import { searchCustomers, getCustomer } from "../api/client";

export default function CustomerSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceRef = useRef(null);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!query.trim()) {
      setResults([]);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchCustomers(query);
        setResults(res.data.customers || []);
        setShowDropdown(true);
      } catch {
        setResults([]);
      }
      setLoading(false);
    }, 300);
  }, [query]);

  const handleSelect = async (customerId) => {
    setShowDropdown(false);
    setQuery(customerId);
    try {
      const res = await getCustomer(customerId);
      onSelect(res.data);
    } catch {
      onSelect(null);
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Search Customer
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
          placeholder="Search by Customer ID, occupation, or city..."
          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-bank-500 focus:border-bank-500 outline-none transition-all text-sm"
        />
        {loading && (
          <span className="absolute right-6 top-[3.2rem] text-xs text-gray-400">
            Searching...
          </span>
        )}
      </div>

      {showDropdown && results.length > 0 && (
        <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-72 overflow-y-auto">
          {results.map((c) => (
            <button
              key={c.customer_id}
              onClick={() => handleSelect(c.customer_id)}
              className="w-full text-left px-4 py-3 hover:bg-bank-50 border-b border-gray-100 last:border-0 transition-colors"
            >
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-800">
                  {c.customer_id}
                </span>
                <span className="text-sm text-gray-500">{c.city}</span>
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {c.occupation} &middot; ${c.annual_income?.toLocaleString()} &middot;{" "}
                {c.marital_status}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
