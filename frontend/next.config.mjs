/** @type {import('next').NextConfig} */
const config = {
  trailingSlash: true,
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_PROXY ?? 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

export default config
