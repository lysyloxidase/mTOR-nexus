import type { Metadata } from "next";
import Link from "next/link";
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
      <body>
        <header className="site-header">
          <Link className="brand" href="/">mTOR<span>-NEXUS</span></Link>
          <nav aria-label="Primary navigation">
            <Link href="/graph">3D atlas</Link>
            <Link href="/module/1">SBGN modules</Link>
            <Link href="/disease/cancer">Disease</Link>
            <Link href="/drug/sirolimus">Drugs</Link>
            <Link href="/predict">Predict</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
