/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // Désactiver ESLint et TypeScript checks pendant le build
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Vos autres configurations...
}

module.exports = nextConfig