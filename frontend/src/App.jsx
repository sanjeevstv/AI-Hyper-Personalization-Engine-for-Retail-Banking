import { useState } from "react";
import Dashboard from "./components/Dashboard";
import SetupPanel from "./components/SetupPanel";

export default function App() {
  const [initialized, setInitialized] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-bank-800 to-bank-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center text-xl font-bold">
              B
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Banking Personalization Engine
              </h1>
              <p className="text-sm text-blue-200">
                AI-Powered Hyper-Personalization for Retail Banking
              </p>
            </div>
          </div>
          {initialized && (
            <span className="text-xs bg-green-500/20 text-green-200 px-3 py-1 rounded-full border border-green-400/30">
              System Active
            </span>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {!initialized ? (
          <SetupPanel onComplete={() => setInitialized(true)} />
        ) : (
          <Dashboard />
        )}
      </main>
    </div>
  );
}
