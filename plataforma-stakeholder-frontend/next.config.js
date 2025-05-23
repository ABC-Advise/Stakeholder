/** @type {import('next').NextConfig} */
const nextConfig = {
    webpack: (config, { isServer }) => {
        if (!isServer) {
            config.module.rules.push({
                test: /\.worker\.js$/,
                use: {
                    loader: 'worker-loader',
                    options: {
                        filename: 'static/[hash].worker.js',
                        publicPath: '/_next/',
                    },
                },
            })
        }
        return config
    },
}

module.exports = nextConfig 