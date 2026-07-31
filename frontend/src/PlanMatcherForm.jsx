import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./PlanMatcherForm.css";

const API_BASE = "http://localhost:5050";

const METAL_COLORS = {
  Bronze: "#B08968",
  "Expanded Bronze": "#B08968",
  Silver: "#8896A6",
  Gold: "#C9A227",
};

export default function PlanMatcherForm() {
  const [form, setForm] = useState({
    zip_code: "",
    age: "",
    income: "",
    household_size: "",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zip_code: form.zip_code,
          age: form.age,
          income: Number(form.income),
          household_size: Number(form.household_size),
          explain: true,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || `Request failed with status ${res.status}`);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="matcher">
      <h1>NC Affordable Care Act Plan Matcher</h1>
      <p className="subhead">A stress-free way to find and compare marketplace plans with your subsidy applied.</p>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="field-grid">
            <div className="field">
              <label htmlFor="zip_code">ZIP code</label>
              <input
                id="zip_code"
                name="zip_code"
                type="text"
                value={form.zip_code}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="age">Age</label>
              <input
                id="age"
                name="age"
                type="text"
                value={form.age}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="income">Annual household income ($)</label>
              <input
                id="income"
                name="income"
                type="number"
                className="no-spinner"
                value={form.income}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="household_size">Household size</label>
              <input
                id="household_size"
                name="household_size"
                type="number"
                className="no-spinner"
                value={form.household_size}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "Matching..." : "Find plans"}
          </button>
        </form>

        {error && <div className="error-banner">{error}</div>}
      </div>

      {result && (
        <div className="results">
          <div className="results-summary">
            <div className="stat">
              <div className="stat-label">Rating area</div>
              <div className="stat-value">{result.rating_area}</div>
            </div>
            <div className="stat">
              <div className="stat-label">FPL %</div>
              <div className="stat-value">{result.fpl_percentage}%</div>
            </div>
            <div className="stat positive">
              <div className="stat-label">Monthly subsidy</div>
              <div className="stat-value">${result.monthly_subsidy}</div>
            </div>
            <div className="stat">
              <div className="stat-label">Plans found</div>
              <div className="stat-value">{result.plan_count}</div>
            </div>
          </div>

          {result.explanation && (
            <div className="explanation-block">
              <h3>Plan explanation</h3>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.explanation}
              </ReactMarkdown>
            </div>
          )}

          {result.explanation_error && (
            <div className="error-banner">
              Explanation unavailable: {result.explanation_error}
            </div>
          )}

          <div className="plans-list">
            <p className="plans-heading">Matching plans</p>
            {result.matching_plans.map((plan) => (
              <div
                key={plan.StandardComponentId}
                className="plan-row"
                style={{ "--metal-color": METAL_COLORS[plan.MetalLevel] || "#E2E8F0" }}
              >
                <div className="plan-info">
                  <div className="plan-name">{plan.PlanMarketingName}</div>
                  <div className="plan-meta">
                    <span
                      className="metal-tag"
                      style={{
                        background: `${METAL_COLORS[plan.MetalLevel] || "#E2E8F0"}22`,
                        color: METAL_COLORS[plan.MetalLevel] || "#64748B",
                      }}
                    >
                      {plan.MetalLevel}
                    </span>
                    {plan.IssuerMarketPlaceMarketingName}
                  </div>
                </div>
                <div className="plan-price">
                  <div className="price-after">${plan.MonthlyPremiumAfterSubsidy.toFixed(2)}/mo</div>
                  <div className="price-before">was ${plan.IndividualRate.toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
