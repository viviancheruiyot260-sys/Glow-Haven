/** Inline SVG placeholder when a remote product image fails to load. */
export const PRODUCT_IMAGE_FALLBACK =
  "data:image/svg+xml," +
  encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#fdf8f6"/>
      <stop offset="100%" style="stop-color:#e8a4b8"/>
    </linearGradient>
  </defs>
  <rect width="600" height="600" fill="url(#g)"/>
  <text x="50%" y="48%" text-anchor="middle" font-family="Georgia,serif" font-size="28" fill="#c76b8a">Glow Haven</text>
  <text x="50%" y="56%" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#6b5d61">Image unavailable</text>
</svg>`);
