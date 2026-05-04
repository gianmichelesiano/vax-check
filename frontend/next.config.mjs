const isExport = process.env.NEXT_EXPORT === 'true'

/** @type {import('next').NextConfig} */
const config = {
  ...(isExport ? { output: 'export' } : {}),
  trailingSlash: true,
  images: { unoptimized: true },
}

export default config
