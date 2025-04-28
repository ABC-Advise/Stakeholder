/** @type {import('next').NextConfig} */
const nextConfig = {
    transpilePackages: ['@react-sigma/core'],
    experimental: {
        esmExternals: 'loose'
    }
}

export default nextConfig
