"use client";

import { FormEvent, useEffect, useState } from "react";

type TargetAudit = {
  target: string;
  compound_count: number;
  label_count: number;
  ready: boolean;
};

type AIStatus = {
  scientific_release_ready: boolean;
  selectivity_gnn: {
    release_status: string;
    blocking_reasons: string[];
    target_audit: TargetAudit[];
  };
};

type PredictionBundle = {
  selectivity: {
    status: string;
    standardized_smiles: string | null;
    refusal_reason: string | null;
    message: string;
    applicability_domain: {
      in_domain: boolean;
      nearest_similarity: number;
      threshold: number;
    } | null;
  };
  resistance: {
    liabilities: Array<{ mutation_id: string; domain: string; effect: string }>;
    combinations: Array<{ partner: string; rationale: string }>;
  };
  cofolding: {
    status: string;
    message: string;
    boltz_yaml_template: string | null;
    required_experimental_validation: boolean;
  } | null;
};

const API_ROOT = process.env.NEXT_PUBLIC_MTOR_NEXUS_API_URL ?? "http://localhost:8000";

export function PredictionWorkbench() {
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [smiles, setSmiles] = useState("CC1=CC=C(C=C1)C");
  const [bindingMode, setBindingMode] = useState("atp_competitive");
  const [includeCofolding, setIncludeCofolding] = useState(false);
  const [result, setResult] = useState<PredictionBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    fetch("/data/ai-status.json")
      .then((response) => response.json() as Promise<AIStatus>)
      .then(setStatus)
      .catch(() => setError("Could not load the committed AI readiness report."));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const response = await fetch(`${API_ROOT}/ai/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          smiles,
          binding_mode: bindingMode,
          include_cofolding: includeCofolding,
        }),
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setResult((await response.json()) as PredictionBundle);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Prediction request failed.");
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="predict-main">
      <section className="predict-heading">
        <p className="eyebrow">Phase 6 prerelease</p>
        <h1>AI triage, with the brakes visible.</h1>
        <p className="lede">
          The interface is live, but numerical pIC50 prediction remains locked until the
          five-target model passes its registered scientific gates.
        </p>
      </section>

      <section className="release-panel">
        <div>
          <p className="panel-kicker">Selectivity release status</p>
          <h2>{status?.selectivity_gnn.release_status ?? "loading"}</h2>
        </div>
        <span className="red-tag">
          {status?.scientific_release_ready ? "validated" : "not validated for scoring"}
        </span>
        {status?.selectivity_gnn.blocking_reasons.map((reason) => <p key={reason}>{reason}</p>)}
        <div className="audit-grid">
          {status?.selectivity_gnn.target_audit.map((target) => (
            <article key={target.target}>
              <strong>{target.target}</strong>
              <span>{target.compound_count} compounds</span>
              <small>{target.label_count} labels</small>
            </article>
          ))}
        </div>
      </section>

      <section className="prediction-layout">
        <form className="predict-form" onSubmit={submit}>
          <p className="panel-kicker">Research query</p>
          <label>
            SMILES
            <textarea value={smiles} onChange={(event) => setSmiles(event.target.value)} />
          </label>
          <label>
            Binding mode
            <select value={bindingMode} onChange={(event) => setBindingMode(event.target.value)}>
              <option value="frb_allosteric">FRB allosteric</option>
              <option value="atp_competitive">ATP competitive</option>
              <option value="dual_pi3k_mtor_atp">Dual PI3K-mTOR ATP</option>
              <option value="bisteric_frb_atp">Bi-steric FRB + ATP</option>
              <option value="rictor_mtor_association">RICTOR-mTOR association</option>
            </select>
          </label>
          <label className="checkbox-row">
            <input
              checked={includeCofolding}
              onChange={(event) => setIncludeCofolding(event.target.checked)}
              type="checkbox"
            />
            Prepare external Boltz-2 handoff
          </label>
          <button disabled={pending} type="submit">{pending ? "Assessing..." : "Run triage"}</button>
          {error && <p className="error-text">{error}</p>}
        </form>

        <div className="result-stack">
          {!result && <article className="result-panel muted">Submit a molecule to run triage.</article>}
          {result && (
            <>
              <article className="result-panel">
                <p className="panel-kicker">Selectivity GNN</p>
                <h2>{result.selectivity.status}</h2>
                <span className="red-tag">{result.selectivity.refusal_reason}</span>
                <p>{result.selectivity.message}</p>
                {result.selectivity.applicability_domain && (
                  <small>
                    Nearest-neighbor Tanimoto:{" "}
                    {result.selectivity.applicability_domain.nearest_similarity.toFixed(3)}; threshold:{" "}
                    {result.selectivity.applicability_domain.threshold.toFixed(1)}
                  </small>
                )}
              </article>
              <article className="result-panel">
                <p className="panel-kicker">Resistance triage</p>
                <h2>Computational liabilities</h2>
                {result.resistance.liabilities.length === 0 && <p>No mapped structural liability.</p>}
                {result.resistance.liabilities.map((liability) => (
                  <p key={liability.mutation_id}>
                    <strong>{liability.mutation_id}</strong> ({liability.domain}): {liability.effect}
                  </p>
                ))}
                {result.resistance.combinations.map((combination) => (
                  <p key={combination.partner}>
                    <strong>Combination hypothesis: {combination.partner}</strong><br />
                    {combination.rationale}
                  </p>
                ))}
              </article>
              {result.cofolding && (
                <article className="result-panel">
                  <p className="panel-kicker">Boltz-2 cofolding handoff</p>
                  <h2>{result.cofolding.status}</h2>
                  <p>{result.cofolding.message}</p>
                  <pre>{result.cofolding.boltz_yaml_template}</pre>
                </article>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  );
}
