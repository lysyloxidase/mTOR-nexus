import { DiseaseOverlay } from "@/components/disease/DiseaseOverlay";

const diseaseIds = [
  "cancer",
  "mtoropathies_epilepsy",
  "neurodegeneration",
  "aging_longevity",
  "metabolic",
  "rare_syndromes",
  "immunology_transplant",
  "cardiovascular",
];

export function generateStaticParams() {
  return diseaseIds.map((id) => ({ id }));
}

export default async function DiseasePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="detail-main">
      <section className="detail-heading">
        <p className="eyebrow">Phase 4 disease layer</p>
        <h1>Disease overlay</h1>
      </section>
      <DiseaseOverlay diseaseId={id} standalone />
    </main>
  );
}
