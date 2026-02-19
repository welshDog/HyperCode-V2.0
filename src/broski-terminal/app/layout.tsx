
import "./styles/hypercode.css";
import CodeRain from "./components/CodeRain";
import { Providers } from "./components/Providers";

export const metadata = {
  title: "Broski Terminal",
  description: "Hyper Agents Control Room",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="hc-container">
            <CodeRain />
            <header className="hc-header">
              <h1 className="hc-title">&gt; SYSTEM INITIALIZED</h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '12px', color: '#666' }}>NET:</span>
                <span style={{ color: '#00ff88', fontWeight: 'bold' }}>ONLINE</span>
                <div style={{
                  width: '10px',
                  height: '10px',
                  background: '#00ff88',
                  borderRadius: '50%',
                  boxShadow: '0 0 10px #00ff88',
                  animation: 'pulse 2s infinite'
                }} />
              </div>
            </header>
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
