import type { SpeciesEvidence, Tier } from "@/lib/schema";

const tierLabels: Record<Tier, string> = {
  robust: "Robust",
  plausible: "Plausible",
  speculative: "Speculative",
};

export function TierSpeciesBadge({
  tier,
  species,
}: {
  tier: Tier;
  species: SpeciesEvidence[];
}) {
  return (
    <span className="badge-row">
      <span className={`tier-badge tier-${tier}`}>
        <span className="tier-dot" aria-hidden="true" />
        {tierLabels[tier]}
      </span>
      {species.slice(0, 2).map((item) => (
        <span className="species-pill" key={item}>{item.replaceAll("_", " ")}</span>
      ))}
    </span>
  );
}
