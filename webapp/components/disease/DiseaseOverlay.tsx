"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { DiseaseDocument } from "@/lib/schema";
import { useMTORStore } from "@/store/mtor";
import { TierSpeciesBadge } from "@/components/ui/TierSpeciesBadge";

export function DiseaseOverlay({
  diseaseId,
  standalone = false,
}: {
  diseaseId?: string;
  standalone?: boolean;
}) {
  const [document, setDocument] = useState<DiseaseDocument | null>(null);
  const selectedDisease = useMTORStore((state) => state.selectedDisease);
  const selectDisease = useMTORStore((state) => state.selectDisease);
  const activeId = diseaseId ?? selectedDisease;
  useEffect(() => {
    fetch("/data/diseases.json")
      .then((response) => response.json() as Promise<DiseaseDocument>)
      .then(setDocument);
  }, []);
  useEffect(() => {
    if (diseaseId) selectDisease(diseaseId);
  }, [diseaseId, selectDisease]);
  const disease = useMemo(
    () => document?.disease_classes.find((candidate) => candidate.disease_id === activeId),
    [activeId, document],
  );
  const mutations = useMemo(
    () => document?.mutations.filter((mutation) => disease?.key_nodes.includes(mutation.gene_symbol)) ?? [],
    [disease, document],
  );
  return (
    <section className={`disease-overlay ${standalone ? "disease-overlay-standalone" : ""}`}>
      <p className="panel-kicker">Disease overlay</p>
      {!diseaseId && (
        <label className="disease-selector">
          Disease class
          <select value={activeId ?? ""} onChange={(event) => selectDisease(event.target.value || null)}>
            <option value="">None</option>
            {document?.disease_classes.map((candidate) => (
              <option key={candidate.disease_id} value={candidate.disease_id}>{candidate.title}</option>
            ))}
          </select>
        </label>
      )}
      {disease ? (
        <>
          <div className="disease-title">
            <h2>{disease.title}</h2>
            {!standalone && <Link href={`/disease/${disease.disease_id}`}>Details</Link>}
          </div>
          <TierSpeciesBadge species={disease.species_evidence} tier={disease.tier} />
          <p>{disease.mechanism}</p>
          {disease.species_caveat && <p className="caveat-banner">{disease.species_caveat}</p>}
          <div className="disease-node-list">
            {disease.key_nodes.map((node) => <span key={node}>{node}</span>)}
          </div>
          {!!disease.cohort_frequencies.length && (
            <div className="disease-section">
              <strong>Derived cohort frequency</strong>
              {disease.cohort_frequencies.map((frequency) => (
                <p key={frequency.cohort}>
                  <a href={frequency.source_url} target="_blank" rel="noreferrer">{frequency.gene_symbol}</a>
                  {" "}{frequency.altered_cases}/{frequency.profiled_cases} ({frequency.frequency_percent.toFixed(1)}%)
                  <small>{frequency.cohort}</small>
                </p>
              ))}
            </div>
          )}
          {!!mutations.length && (
            <div className="disease-section">
              <strong>Key mutations</strong>
              {mutations.map((mutation) => (
                <span className="mutation-row" key={mutation.mutation_id}>
                  {mutation.gene_symbol} {mutation.hgvs_protein ?? mutation.hgvs_coding}
                </span>
              ))}
            </div>
          )}
          {!!disease.approved_drugs.length && (
            <div className="disease-section">
              <strong>Approved interventions</strong>
              {disease.approved_drugs.map((drug) => (
                <a href={drug.source_url} key={`${drug.name}-${drug.indication}`} target="_blank" rel="noreferrer">
                  {drug.name}: {drug.indication}
                </a>
              ))}
            </div>
          )}
          {!!disease.trial_links.length && (
            <div className="disease-section">
              <strong>ClinicalTrials.gov</strong>
              {disease.trial_links.map((trial) => (
                <a href={trial.url} key={trial.nct_id} target="_blank" rel="noreferrer">{trial.nct_id}: {trial.title}</a>
              ))}
            </div>
          )}
          {standalone && disease.disease_id === "rare_syndromes" && (
            <div className="syndrome-grid">
              {disease.rare_syndromes.map((syndrome) => (
                <article key={syndrome.syndrome_id}>
                  <h3>{syndrome.syndrome_id.replaceAll("_", " ")}</h3>
                  <p><strong>Genes</strong> {syndrome.genes.join(", ")}</p>
                  {syndrome.drug && <p><strong>Drug</strong> {syndrome.drug}</p>}
                  {syndrome.omim && <p><strong>OMIM</strong> {syndrome.omim}</p>}
                  {syndrome.recurrent_variant && <p><strong>Variant</strong> {syndrome.recurrent_variant}</p>}
                </article>
              ))}
            </div>
          )}
        </>
      ) : <p>Select a disease class to highlight perturbed pathway nodes and edges.</p>}
    </section>
  );
}
