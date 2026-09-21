import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MossGuard — AI Agent Trust & Guardrail System",
  description:
    "Real-time AI agent response validation. Catches hallucinations by fact-checking claims against a knowledge base with sub-10ms Moss retrieval.",
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
