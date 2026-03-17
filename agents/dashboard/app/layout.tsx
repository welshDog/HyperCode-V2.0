import type { Metadata } from "next";
import { JetBrains_Mono, Orbitron } from "next/font/google";
import "./globals.css";
import "./themes/sensory-themes.css";
import { SensoryThemeProvider } from "./themes/SensoryThemeProvider";

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  variable: "--font-orbitron",
});

export const metadata: Metadata = {
  title: "HyperStation | Mission Control",
  description: "Advanced Multi-Agent Orchestration Dashboard for neurodivergent-first development",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${mono.variable} ${orbitron.variable} antialiased bg-[#050505] text-cyan-500 overflow-hidden`}
      >
        {/* Skip navigation — WCAG 2.4.1: keyboard users jump straight to content */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[9999] focus:px-4 focus:py-2 focus:bg-cyan-500 focus:text-black focus:rounded focus:font-bold focus:outline-none"
        >
          Skip to main content
        </a>

        {/* Decorative background — hidden from assistive technology */}
        <div
          className="fixed inset-0 pointer-events-none z-0"
          role="presentation"
          aria-hidden="true"
        >
          <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,18,0)_1px,transparent_1px),linear-gradient(90deg,rgba(18,18,18,0)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-20"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-cyan-900/10 via-[#050505] to-[#050505]"></div>
        </div>

        {/* Main content landmark — all page content must live inside this */}
        <main
          id="main-content"
          role="main"
          aria-label="HyperStation Mission Control Dashboard"
          className="relative z-10 h-screen w-screen flex flex-col"
          tabIndex={-1}
        >
          <SensoryThemeProvider>{children}</SensoryThemeProvider>
        </main>
      </body>
    </html>
  );
}
