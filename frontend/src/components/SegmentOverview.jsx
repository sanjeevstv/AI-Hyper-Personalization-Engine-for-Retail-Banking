import { useEffect, useState } from "react";
import {
  getSegmentsOverview,
  getFilterOptions,
  getFilteredCustomers,
  exportCustomersCSV,
} from "../api/client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const COLORS = [
  "#2563eb", "#7c3aed", "#059669", "#d97706", "#dc2626",
  "#0891b2", "#4f46e5", "#16a34a", "#ea580c", "#be185d",
];

export default function SegmentOverview() {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [options, setOptions] = useState({ cities: [], occupations: [] });

  const [subFilters, setSubFilters] = useState({
    city: "",
    occupation: "",
    age_min: "",
    age_max: "",
  });

  const [drillDown, setDrillDown] = useState(null);
  const [drillCustomers, setDrillCustomers] = useState([]);
  const [drillLoading, setDrillLoading] = useState(false);

  useEffect(() => {
    Promise.all([getSegmentsOverview(), getFilterOptions()])
      .then(([seg, opts]) => {
        setSegments(seg.data);
        setOptions(opts.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const buildDrillFilters = (segmentName) => {
    const f = { segment: segmentName };
    if (subFilters.city) f.city = subFilters.city;
    if (subFilters.occupation) f.occupation = subFilters.occupation;
    if (subFilters.age_min) f.age_min = subFilters.age_min;
    if (subFilters.age_max) f.age_max = subFilters.age_max;
    return f;
  };

  const handleCardClick = async (segmentName) => {
    if (drillDown === segmentName) {
      setDrillDown(null);
      return;
    }
    setDrillDown(segmentName);
    setDrillLoading(true);
    try {
      const res = await getFilteredCustomers(buildDrillFilters(segmentName));
      setDrillCustomers(res.data.customers || []);
    } catch {
      setDrillCustomers([]);
    }
    setDrillLoading(false);
  };

  const handleSubFilterApply = async () => {
    if (!drillDown) return;
    setDrillLoading(true);
    try {
      const res = await getFilteredCustomers(buildDrillFilters(drillDown));
      setDrillCustomers(res.data.customers || []);
    } catch {
      setDrillCustomers([]);
    }
    setDrillLoading(false);
  };

  const handleExport = () => {
    if (!drillDown) return;
    exportCustomersCSV(buildDrillFilters(drillDown));
  };

  const set = (key) => (e) =>
    setSubFilters((f) => ({ ...f, [key]: e.target.value }));

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <p className="text-sm text-gray-400">Loading segment data...</p>
      </div>
    );
  }

  if (segments.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <p className="text-sm text-gray-400 italic">
          No segment data available. Run segmentation first.
        </p>
      </div>
    );
  }

  const total = segments.reduce((sum, s) => sum + s.customer_count, 0);
  const inputCls =
    "w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-bank-500 focus:border-bank-500 outline-none";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        {segments.map((seg, idx) => (
          <button
            key={seg.segment_name}
            onClick={() => handleCardClick(seg.segment_name)}
            className={`bg-white rounded-xl shadow-sm border p-4 text-center min-w-[130px] transition-all hover:shadow-md cursor-pointer ${
              drillDown === seg.segment_name
                ? "border-bank-500 ring-2 ring-bank-200"
                : "border-gray-200"
            }`}
          >
            <div
              className="w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center text-white font-bold text-sm"
              style={{ backgroundColor: COLORS[idx % COLORS.length] }}
            >
              {seg.customer_count}
            </div>
            <div className="text-sm font-semibold text-gray-800 truncate">
              {seg.segment_name}
            </div>
            <div className="text-xs text-gray-500">
              {((seg.customer_count / total) * 100).toFixed(1)}%
            </div>
          </button>
        ))}
      </div>

      {drillDown && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-md font-bold text-gray-800">
              Customers in &ldquo;{drillDown}&rdquo;
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({drillCustomers.length})
              </span>
            </h4>
            <button
              onClick={handleExport}
              className="px-4 py-1.5 bg-bank-600 hover:bg-bank-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Export to CSV
            </button>
          </div>

          <div className="flex flex-wrap gap-3 items-end p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="flex-1 min-w-[120px]">
              <label className="block text-xs text-gray-500 mb-1">City</label>
              <select value={subFilters.city} onChange={set("city")} className={inputCls}>
                <option value="">All</option>
                {options.cities.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[120px]">
              <label className="block text-xs text-gray-500 mb-1">Occupation</label>
              <select value={subFilters.occupation} onChange={set("occupation")} className={inputCls}>
                <option value="">All</option>
                {options.occupations.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>
            <div className="min-w-[80px]">
              <label className="block text-xs text-gray-500 mb-1">Min Age</label>
              <input
                type="number" min="0" max="120" placeholder="22"
                value={subFilters.age_min} onChange={set("age_min")}
                className={inputCls}
              />
            </div>
            <div className="min-w-[80px]">
              <label className="block text-xs text-gray-500 mb-1">Max Age</label>
              <input
                type="number" min="0" max="120" placeholder="65"
                value={subFilters.age_max} onChange={set("age_max")}
                className={inputCls}
              />
            </div>
            <button
              onClick={handleSubFilterApply}
              className="px-4 py-1.5 bg-gray-700 hover:bg-gray-800 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Apply
            </button>
          </div>

          {drillLoading ? (
            <p className="text-sm text-gray-400">Loading...</p>
          ) : drillCustomers.length === 0 ? (
            <p className="text-sm text-gray-400 italic">
              No customers match the filters.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-left text-xs uppercase text-gray-500">
                    <th className="py-2 px-3">Customer ID</th>
                    <th className="py-2 px-3">Age</th>
                    <th className="py-2 px-3">Occupation</th>
                    <th className="py-2 px-3">City</th>
                    <th className="py-2 px-3">Annual Income</th>
                    <th className="py-2 px-3">Segment</th>
                  </tr>
                </thead>
                <tbody>
                  {drillCustomers.map((c) => (
                    <tr
                      key={c.customer_id}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-2 px-3 font-medium text-bank-700">
                        {c.customer_id}
                      </td>
                      <td className="py-2 px-3">{c.age}</td>
                      <td className="py-2 px-3">{c.occupation}</td>
                      <td className="py-2 px-3">{c.city}</td>
                      <td className="py-2 px-3">
                        ${c.annual_income?.toLocaleString()}
                      </td>
                      <td className="py-2 px-3">
                        <span className="px-2 py-0.5 bg-bank-50 text-bank-700 rounded-full text-xs">
                          {c.segment_name || "\u2014"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            Segment Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={segments}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="segment_name"
                tick={{ fontSize: 11 }}
                interval={0}
                angle={-20}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar
                dataKey="customer_count"
                name="Customers"
                radius={[6, 6, 0, 0]}
              >
                {segments.map((_, idx) => (
                  <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            Segment Share
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={segments}
                dataKey="customer_count"
                nameKey="segment_name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ segment_name, percent }) =>
                  `${segment_name} (${(percent * 100).toFixed(0)}%)`
                }
                labelLine={true}
              >
                {segments.map((_, idx) => (
                  <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
