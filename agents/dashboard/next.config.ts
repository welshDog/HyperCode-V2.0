import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    turbo: {
      // Resolve the project root to handle multiple lockfiles
      root: path.resolve(__dirname, '../../'),
    },
  },
};

export default nextConfig;
