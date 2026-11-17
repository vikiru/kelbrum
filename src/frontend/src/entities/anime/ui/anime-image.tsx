import { ImageOff } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';

import { Skeleton } from '@/shared/components/ui/skeleton';
import { imageSrcSet } from '@/shared/lib/responsive-image-srcset';

export interface AnimeImageProps {
  images: AnimeCardItem['images'];
  alt: string;
  className?: string;
  sizes?: string;
  loading?: 'eager' | 'lazy';
  fetchPriority?: 'high' | 'low' | 'auto';
  showSkeleton?: boolean;
}

interface ImageState {
  sourceKey: string;
  useWebp: boolean;
  failed: boolean;
  loaded: boolean;
}

export function AnimeImage({
  images,
  alt,
  className,
  sizes,
  loading = 'lazy',
  fetchPriority = 'auto',
  showSkeleton = true,
}: AnimeImageProps) {
  const webp = images?.webp;
  const jpg = images?.jpg;
  const webpUrl = webp?.large_image_url ?? webp?.image_url ?? null;
  const jpgUrl = jpg?.large_image_url ?? jpg?.image_url ?? null;
  const sourceKey = `${webpUrl ?? ''}|${jpgUrl ?? ''}`;
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [imageState, setImageState] = useState<ImageState>(() => createImageState(sourceKey, webpUrl, jpgUrl));

  const currentImageState =
    imageState.sourceKey === sourceKey ? imageState : createImageState(sourceKey, webpUrl, jpgUrl);
  const { useWebp, failed, loaded } = currentImageState;
  const activeSrc = (useWebp ? (webpUrl ?? jpgUrl) : (jpgUrl ?? webpUrl)) || undefined;

  useEffect(() => {
    const image = imageRef.current;
    if (failed || !activeSrc || !image?.complete || image.naturalWidth <= 0) return;
    setImageState((current) => {
      if (current.sourceKey !== sourceKey) {
        return { ...createImageState(sourceKey, webpUrl, jpgUrl), loaded: true };
      }
      return current.loaded ? current : { ...current, loaded: true };
    });
  }, [activeSrc, failed, jpgUrl, sourceKey, webpUrl]);

  if (failed)
    return (
      <div
        className={`flex items-center justify-center bg-muted text-muted-foreground ${className ?? ''}`}
        aria-label={`${alt} unavailable`}
      >
        <ImageOff className="icon-lg" aria-hidden="true" />
      </div>
    );

  return (
    <>
      {showSkeleton && !loaded && <Skeleton className="absolute inset-0 z-1 rounded-none" aria-hidden="true" />}

      <picture className="block h-full w-full">
        {useWebp && webp && <source type="image/webp" srcSet={imageSrcSet(webp)} sizes={sizes} />}
        <img
          ref={imageRef}
          src={activeSrc}
          srcSet={useWebp ? imageSrcSet(webp) : imageSrcSet(jpg)}
          sizes={sizes}
          alt={alt}
          loading={loading}
          fetchPriority={fetchPriority}
          decoding="async"
          className={`${className ?? ''} ${loaded ? '' : 'opacity-0'}`}
          onLoad={() => setImageState({ sourceKey, useWebp, failed: false, loaded: true })}
          onError={() => {
            if (useWebp && jpgUrl) {
              setImageState({ sourceKey, useWebp: false, failed: false, loaded: false });
            } else setImageState({ sourceKey, useWebp, failed: true, loaded: false });
          }}
        />
      </picture>
    </>
  );
}

function createImageState(sourceKey: string, webpUrl: string | null, jpgUrl: string | null): ImageState {
  return {
    sourceKey,
    useWebp: Boolean(webpUrl),
    failed: !webpUrl && !jpgUrl,
    loaded: false,
  };
}
