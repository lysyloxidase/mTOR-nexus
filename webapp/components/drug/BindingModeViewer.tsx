"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { BindingMode, DrugDocument } from "@/lib/schema";
import { TierSpeciesBadge } from "@/components/ui/TierSpeciesBadge";

const activeSites = (bindingMode?: BindingMode) =>
  bindingMode === "bisteric_frb_atp"
    ? ["frb", "atp"]
    : bindingMode === "frb_allosteric"
      ? ["frb"]
      : bindingMode === "rictor_mtor_association" ? ["mtorc2"] : ["atp"];

export function BindingModeViewer({ drugId }: { drugId: string }) {
  const [document, setDocument] = useState<DrugDocument | null>(null);
  useEffect(() => {
    fetch("/data/drugs.json")
      .then((response) => response.json() as Promise<DrugDocument>)
      .then(setDocument);
  }, []);
  const drug = useMemo(
    () => document?.drugs.find((candidate) => candidate.drug_id === drugId),
    [document, drugId],
  );
  const generation = useMemo(
    () => document?.generations.find((candidate) => candidate.generation_id === drug?.generation_id),
    [document, drug],
  );
  const siteIds = useMemo(() => activeSites(generation?.binding_mode), [generation]);
  const sites = useMemo(
    () => document?.structural_sites.filter((site) => siteIds.includes(site.site_id)) ?? [],
    [document, siteIds],
  );
  const mutations = useMemo(
    () => document?.resistance_mutations.filter((mutation) => siteIds.includes(mutation.site_id)) ?? [],
    [document, siteIds],
  );
  const links = useMemo(
    () => document?.target_links.filter((link) => link.drug_id === drugId) ?? [],
    [document, drugId],
  );
  const compound = useMemo(
    () => document?.bioactivity.find((candidate) => candidate.drug_id === drugId),
    [document, drugId],
  );
  const counts = useMemo(
    () => new Map(
      document?.counter_screen_targets.map((target) => [
        target.gene_symbol,
        compound?.activities.filter((activity) => activity.target_gene_symbol === target.gene_symbol).length ?? 0,
      ]) ?? [],
    ),
    [compound, document],
  );
  const pdbId = sites[0]?.pdb_id ?? "4JSV";
  if (!document || !drug || !generation) return <p className="muted">Loading inhibitor layer...</p>;
  return (
    <section className="binding-layout">
      <aside className="drug-sidebar">
        <p className="panel-kicker">Phase 5 inhibitor catalog</p>
        {document.generations.map((group) => (
          <section className="drug-group" key={group.generation_id}>
            <strong>{group.title}</strong>
            {group.drug_ids.map((id) => (
              <Link className={id === drugId ? "active" : ""} href={`/drug/${id}`} key={id}>{id}</Link>
            ))}
          </section>
        ))}
      </aside>
      <div className="binding-content">
        <section className="drug-summary">
          <p className="panel-kicker">{generation.title}</p>
          <h2>{drug.name}</h2>
          <p>{drug.mechanism}</p>
          <a href={`https://www.ebi.ac.uk/chembl/explore/compound/${drug.chembl_id}`} target="_blank" rel="noreferrer">
            {drug.chembl_id}
          </a>
          {!!drug.aliases.length && <p><strong>Aliases</strong> {drug.aliases.join(", ")}</p>}
          {!!drug.approvals.length && <p><strong>Approvals</strong> {drug.approvals.join(", ")}</p>}
          {drug.potency && <p className="potency-note"><strong>Potency</strong> {drug.potency}</p>}
          {drug.off_target && <p className="caveat-banner"><strong>Off-target note</strong> {drug.off_target}</p>}
          {drug.caveat && <p className="caveat-banner">{drug.caveat}</p>}
          {links.map((link) => (
            <div className="drug-target-row" key={link.target_node_id}>
              <strong>{link.mechanism}</strong> {link.target_node_id}
              <TierSpeciesBadge species={link.species_evidence} tier={link.tier} />
            </div>
          ))}
        </section>
        <section className="binding-viewer">
          <div className="structure-toolbar">
            <div>
              <p className="panel-kicker">Mol* binding-mode viewer</p>
              <h2>{generation.binding_site}</h2>
            </div>
            <span>PDB {pdbId}</span>
          </div>
          <iframe
            allow="fullscreen"
            loading="lazy"
            src={`https://molstar.org/viewer/?pdb=${pdbId.toLowerCase()}`}
            title={`Mol* binding-mode viewer for PDB ${pdbId}`}
          />
          <div className="site-map">
            {document.structural_sites.map((site) => (
              <article className={siteIds.includes(site.site_id) ? "active" : ""} key={site.site_id}>
                <i style={{ background: site.color }} />
                <strong>{site.label}</strong>
                <small>{site.domain}</small>
                <p>{site.description}</p>
              </article>
            ))}
          </div>
          {generation.binding_mode === "bisteric_frb_atp" && (
            <p className="bisteric-note">Bi-steric mode highlights both structural sites simultaneously. The map is a mechanistic composite, not a deposited ternary co-complex.</p>
          )}
        </section>
        <section className="drug-detail-grid">
          <article>
            <p className="panel-kicker">Resistance annotation</p>
            {mutations.length ? mutations.map((mutation) => (
              <span className="resistance-row" key={mutation.mutation_id}>
                <i style={{ background: mutation.color }} />
                <strong>{mutation.mutation_id}</strong> {mutation.domain}: {mutation.effect}
              </span>
            )) : <p className="muted">No mapped resistance residues for this mode.</p>}
          </article>
          <article>
            <p className="panel-kicker">ChEMBL counter-screens</p>
            {document.counter_screen_targets.map((target) => (
              <span className="counter-screen-row" key={target.chembl_id}>
                <strong>{target.gene_symbol}</strong>
                <small>{counts.get(target.gene_symbol) ?? 0} IC50/Ki/Kd labels</small>
              </span>
            ))}
          </article>
        </section>
      </div>
    </section>
  );
}
