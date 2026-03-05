import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Experimental options for Next.js 16+
  experimental: {
    // Turbopack root resolution (if supported by this version)
    turbo: {
      root: path.resolve(__dirname, '../../'),
    }
  } as any,
};

export default nextConfig;
