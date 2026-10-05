import { useEffect, useState } from "react";
import { PRODUCT_IMAGE_FALLBACK } from "../constants/images";

export default function ProductImage({ src, alt, className = "", eager = false }) {
  const [currentSrc, setCurrentSrc] = useState(src || PRODUCT_IMAGE_FALLBACK);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setCurrentSrc(src || PRODUCT_IMAGE_FALLBACK);
    setLoaded(false);
  }, [src]);

  return (
    <div className={`product-image-wrap ${loaded ? "is-loaded" : "is-loading"}`}>
      {!loaded && <div className="product-image-shimmer" aria-hidden="true" />}
      <img
        className={className}
        src={currentSrc}
        alt={alt}
        loading={eager ? "eager" : "lazy"}
        decoding="async"
        referrerPolicy="no-referrer"
        onLoad={() => setLoaded(true)}
        onError={() => {
          if (currentSrc !== PRODUCT_IMAGE_FALLBACK) {
            setCurrentSrc(PRODUCT_IMAGE_FALLBACK);
            setLoaded(false);
          } else {
            setLoaded(true);
          }
        }}
      />
    </div>
  );
}
