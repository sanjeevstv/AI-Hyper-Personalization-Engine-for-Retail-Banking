export default function CustomerProfile({ customer }) {
  if (!customer) return null;

  const { customer: info, profile, segment } = customer;

  const infoItems = [
    { label: "Age", value: info.age },
    { label: "Occupation", value: info.occupation },
    { label: "City", value: info.city },
    { label: "Annual Income", value: `$${info.annual_income?.toLocaleString()}` },
    { label: "Marital Status", value: info.marital_status },
  ];

  const profileItems = profile
    ? [
        { label: "Monthly Income", value: `$${profile.monthly_income?.toLocaleString()}` },
        { label: "Monthly Spending", value: `$${profile.monthly_spending?.toLocaleString()}` },
        { label: "Savings Ratio", value: `${(profile.savings_ratio * 100).toFixed(1)}%` },
        { label: "Travel Frequency", value: `${profile.travel_frequency} trips` },
        { label: "Top Category", value: profile.preferred_spending_category },
        { label: "Credit Behavior", value: profile.credit_behavior },
        { label: "Investment Interest", value: profile.investment_interest?.toFixed(1) },
        { label: "Risk Appetite", value: profile.risk_appetite },
        { label: "Preferred Channel", value: profile.preferred_channel },
      ]
    : [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">Customer Profile</h3>
        {segment && (
          <span className="px-3 py-1 bg-bank-100 text-bank-700 text-xs font-semibold rounded-full">
            {segment.segment_name}
          </span>
        )}
      </div>

      <div className="mb-4">
        <span className="text-2xl font-bold text-bank-700">
          {info.customer_id}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {infoItems.map((item) => (
          <div key={item.label}>
            <dt className="text-xs text-gray-500 uppercase tracking-wider">
              {item.label}
            </dt>
            <dd className="text-sm font-medium text-gray-800">{item.value}</dd>
          </div>
        ))}
      </div>

      {profile && (
        <>
          <hr className="my-4 border-gray-100" />
          <h4 className="text-sm font-semibold text-gray-600 mb-3 uppercase tracking-wider">
            Financial Profile
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {profileItems.map((item) => (
              <div key={item.label}>
                <dt className="text-xs text-gray-500">{item.label}</dt>
                <dd className="text-sm font-medium text-gray-800">
                  {item.value}
                </dd>
              </div>
            ))}
          </div>
        </>
      )}

      {!profile && (
        <p className="text-sm text-gray-400 italic mt-2">
          Profile not yet computed.
        </p>
      )}
    </div>
  );
}
