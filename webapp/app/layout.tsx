import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "mTOR-NEXUS",
  description: "A provenance-first interactive mTOR signaling atlas",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
