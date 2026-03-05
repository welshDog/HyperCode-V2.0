import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  // @ts-expect-error - turbopack option is new in Next.js 16
  turbopack: {
    // Resolve the project root to handle multiple lockfiles
    root: path.resolve(__dirname, '../../'),
  },
};

export default nextConfig;
