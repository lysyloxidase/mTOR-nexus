const principles = [
  ["Evidence before confidence", "Every interaction carries a tier and primary citation."],
  ["Species stays visible", "Human, rodent, structural, biochemical, and computational evidence remain distinct."],
  ["Guard the vocabulary", "Known mTOR nomenclature errors fail validation before they reach the atlas."],
];

export default function Home() {
  return (
    <main>
      <section className="hero">
        <p className="eyebrow">Phase 1 foundation</p>
        <h1>mTOR<span>-NEXUS</span></h1>
        <p className="lede">
          A provenance-first interactive atlas of mTOR signaling and a foundation
          for AI-assisted drug discovery.
        </p>
        <div className="actions">
          <a className="primary" href="http://localhost:8000/graph">Explore seed graph</a>
          <a href="https://github.com/lysyloxidase/mtor-nexus">View source</a>
        </div>
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
