interface ImageVariant {
  image_url: string | null;
  small_image_url: string | null;
  large_image_url: string | null;
}

export function imageSrcSet(variant: ImageVariant | null | undefined): string | undefined {
  if (!variant) return undefined;
  const candidates = [
    variant.small_image_url && `${variant.small_image_url} 100w`,
    variant.image_url && `${variant.image_url} 225w`,
    variant.large_image_url && `${variant.large_image_url} 400w`,
  ].filter((candidate): candidate is string => Boolean(candidate));
  return candidates.length > 0 ? candidates.join(', ') : undefined;
}
