export function PlaceholderPage({ phase, title }: { phase: string; title: string }) {
  return (
    <main className="detail-main">
      <section className="detail-heading">
        <p className="eyebrow">{phase}</p>
        <h1>{title}</h1>
        <p className="lede">This route is reserved for the next curated mTOR-NEXUS release.</p>
      </section>
    </main>
  );
}
