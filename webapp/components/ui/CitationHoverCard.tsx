"use client";

import { useState } from "react";
import type { SpeciesEvidence, Tier } from "@/lib/schema";
import { TierSpeciesBadge } from "./TierSpeciesBadge";

interface CrossrefWork {
  message?: { title?: string[]; URL?: string };
}

export function CitationHoverCard({
  doi,
  tier = "robust",
  species = ["human_and_rodent"],
}: {
  doi: string;
  tier?: Tier;
  species?: SpeciesEvidence[];
}) {
  const [title, setTitle] = useState("Curated pathway citation");
  const [loaded, setLoaded] = useState(false);
  const loadMetadata = async () => {
    if (loaded) return;
    setLoaded(true);
    try {
      const response = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`);
      if (!response.ok) return;
      const payload = (await response.json()) as CrossrefWork;
      setTitle(payload.message?.title?.[0] ?? title);
    } catch {
      // The DOI link remains usable when Crossref is unavailable.
    }
  };
  return (
    <span className="citation-hover" onMouseEnter={loadMetadata} onFocus={loadMetadata}>
      <a href={`https://doi.org/${doi}`} target="_blank" rel="noreferrer">{doi}</a>
      <span className="citation-card" role="tooltip">
        <strong>{title}</strong>
        <TierSpeciesBadge tier={tier} species={species} />
      </span>
    </span>
  );
}
