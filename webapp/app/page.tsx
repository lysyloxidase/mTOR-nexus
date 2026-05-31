import Link from "next/link";
import { MTORGraph3D } from "@/components/three/MTORGraph3D";

const principles = [
  ["Dual-scale navigation", "Move from the global 3D pathway to seven publication-oriented SBGN-PD diagrams."],
  ["Evidence remains visible", "Switch localization, tier, and species lenses without flattening the underlying provenance."],
  ["Structure meets signaling", "Open curated phosphosites, protein domains, UniProt accessions, and linked PDB structures."],
];

export default function Home() {
  return (
    <main className="home-main">
      <section className="landing-grid">
        <div className="hero">
          <p className="eyebrow">Phase 3 pathway explorer</p>
          <h1>mTOR<span>-NEXUS</span></h1>
          <p className="lede">
            A provenance-first interactive atlas for navigating mTOR signaling from
            global architecture to evidence-bearing molecular detail.
          </p>
          <div className="actions">
            <Link className="primary" href="/graph">Explore the 3D atlas</Link>
            <Link href="/module/1">Open SBGN modules</Link>
          </div>
        </div>
        <MTORGraph3D compact />
      </section>
      <section className="principles" aria-label="Project principles">
        {principles.map(([title, description]) => (
          <article key={title}>
            <h2>{title}</h2>
            <p>{description}</p>
          </article>
        ))}
      </section>
      <footer>Research software. Not for clinical decision-making.</footer>
    </main>
  );
}
