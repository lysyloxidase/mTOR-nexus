import { PlaceholderPage } from "@/components/ui/PlaceholderPage";

export default async function DrugPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <PlaceholderPage phase="Phase 5" title={`Drug: ${decodeURIComponent(id)}`} />;
}
