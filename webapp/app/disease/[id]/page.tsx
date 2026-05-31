import { PlaceholderPage } from "@/components/ui/PlaceholderPage";

export default async function DiseasePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <PlaceholderPage phase="Phase 4" title={`Disease: ${decodeURIComponent(id)}`} />;
}
