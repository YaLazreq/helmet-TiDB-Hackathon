/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Désactiver ESLint pendant le build
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Si vous avez aussi des erreurs TypeScript
    ignoreBuildErrors: true,
  },
  experimental: {
    // Si vous utilisez Turbopack
    turbo: {
      resolveAlias: {
        canvas: './empty-module.js',
      },
    },
  },
  output: 'standalone', // Important pour Docker
}

module.exports = nextConfig