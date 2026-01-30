import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "huggingface.co",
        pathname: "/front/assets/**",
      },
    ],
  },
};

export default nextConfig;
