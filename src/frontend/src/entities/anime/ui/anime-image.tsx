import { ImageOff } from 'lucide-react';
import { useState } from 'react';

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
  const [imageState, setImageState] = useState<ImageState>(() => createImageState(sourceKey, webpUrl, jpgUrl));

  if (imageState.sourceKey !== sourceKey) {
    setImageState(createImageState(sourceKey, webpUrl, jpgUrl));
  }

  const { useWebp, failed, loaded } = imageState;

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
          ref={(image) => {
            if (image?.complete && image.naturalWidth > 0) setImageState((current) => ({ ...current, loaded: true }));
          }}
          src={(useWebp ? (webpUrl ?? jpgUrl) : (jpgUrl ?? webpUrl)) || undefined}
          srcSet={useWebp ? imageSrcSet(webp) : imageSrcSet(jpg)}
          sizes={sizes}
          alt={alt}
          loading={loading}
          fetchPriority={fetchPriority}
          decoding="async"
          className={`${className ?? ''} ${loaded ? '' : 'opacity-0'}`}
          onLoad={() => setImageState((current) => ({ ...current, loaded: true }))}
          onError={() => {
            if (useWebp && jpgUrl) {
              setImageState((current) => ({ ...current, useWebp: false, loaded: false }));
            } else setImageState((current) => ({ ...current, failed: true }));
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
    failed: !jpgUrl,
    loaded: false,
  };
}
