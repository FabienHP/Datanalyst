import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Datanalyst",
  description: "Datanalyst is your ai-powered data analyst. Generate insights from your data in seconds.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body className={inter.className}>
        {children}
        <div className="banana banana1">🍌</div>
        <div className="banana banana2">🍌</div>
        <div className="banana banana3">🍌</div>
        <div className="banana banana4">🍌</div>
        <div className="banana banana5">🍌</div>
        <div className="banana banana6">🍌</div>
        <div className="banana banana7">🍌</div>
        <div className="banana banana8">🍌</div>
        <div className="banana banana9">🍌</div>
      </body>
    </html>
  );
}
