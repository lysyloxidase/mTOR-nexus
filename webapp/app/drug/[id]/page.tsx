import { BindingModeViewer } from "@/components/drug/BindingModeViewer";

const drugIds = [
  "sirolimus", "temsirolimus", "everolimus", "ridaforolimus", "zotarolimus",
  "torin1", "torin2", "pp242", "azd8055", "vistusertib", "sapanisertib",
  "osi-027", "onatasertib", "gdc-0349", "dactolisib", "gedatolisib",
  "omipalisib", "voxtalisib", "rapalink-1", "rmc-5552", "rmc-6272",
  "rmc-4627", "jr-ab2-011",
];

export function generateStaticParams() {
  return drugIds.map((id) => ({ id }));
}

export default async function DrugPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="detail-main">
      <section className="detail-heading">
        <p className="eyebrow">Three-generation inhibitor pharmacology</p>
        <h1>Binding mode</h1>
      </section>
      <BindingModeViewer drugId={decodeURIComponent(id)} />
    </main>
  );
}
