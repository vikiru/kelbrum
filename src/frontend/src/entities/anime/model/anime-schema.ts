import { z } from 'zod';

export const AnimeImageVariantSchema = z.object({
  image_url: z.string().url().nullable(),
  small_image_url: z.string().url().nullable(),
  large_image_url: z.string().url().nullable(),
});

export const AnimeImagesSchema = z.object({
  jpg: AnimeImageVariantSchema.nullable(),
  webp: AnimeImageVariantSchema.nullable(),
});

export const AnimeCardMetadataSchema = z.object({
  malId: z.number().int().positive(),
  images: AnimeImagesSchema.nullable().optional(),
  title: z.string().min(1),
  titleEnglish: z.string().min(1).nullable(),
  titleJapanese: z.string().min(1).nullable().optional(),
  score: z.number().min(0).max(10).nullable(),
  year: z.number().int().nullable(),
});

export const AnimeCardItemSchema = AnimeCardMetadataSchema;
export const AnimeMetadataSchema = AnimeCardMetadataSchema;

const AnimeResourceSchema = z.object({
  mal_id: z.number().int().positive(),
  name: z.string(),
  type: z.string().nullable().optional(),
  url: z.string().url().nullable().optional(),
});

export const AnimeEntrySchema = z
  .object({
    mal_id: z.number().int().positive(),
    title: z.string().min(1),
    url: z.string().url().nullable(),
    title_english: z.string().nullable(),
    title_japanese: z.string().nullable(),
    type: z.string().nullable(),
    source: z.string().nullable(),
    episodes: z.number().int().nonnegative().nullable(),
    duration: z.string().nullable(),
    durationMinutes: z.number().int().nonnegative().nullable(),
    status: z.string().nullable(),
    year: z.number().int().nullable(),
    rating: z.string().nullable(),
    season: z.string().nullable(),
    score: z.number().min(0).max(10).nullable(),
    synopsis: z.string().nullable(),
    images: AnimeImagesSchema.nullable(),
    trailer: z.object({ url: z.string().url().nullable() }).nullable(),
    genres: z.array(AnimeResourceSchema),
    themes: z.array(AnimeResourceSchema),
    demographics: z.array(AnimeResourceSchema),
    studios: z.array(AnimeResourceSchema),
    recommendations: z
      .array(z.number().int().positive())
      .nullish()
      .transform((value) => value ?? []),
  })
  .strict();

export const AnimeEntryChunkSchema = z.record(z.string(), AnimeEntrySchema);

export const AnimeCardItemsSchema = z.array(AnimeCardItemSchema);

export const AnimeCardMetadataChunkSchema = z.record(z.string(), AnimeCardMetadataSchema);
export const AnimeMetadataChunkSchema = AnimeCardMetadataChunkSchema;

export const AnimeSearchMetadataSchema = AnimeCardItemSchema.extend({
  score: z.number().min(0).max(10).nullable(),
  episodes: z.number().int().nonnegative().nullable(),
  type: z.string().nullable(),
  rating: z.string().nullable(),
  genres: z.array(z.string()),
  themes: z.array(z.string()),
  demographics: z.array(z.string()),
  studios: z.array(z.string()),
});

export const AnimeSearchIndexSchema = z.record(z.string(), AnimeSearchMetadataSchema);

export const AnimeFilterIndexSchema = z.object({
  ids: z.array(z.number().int().positive()),
  numeric: z.record(z.string(), z.array(z.number().nullable())),
  categorical: z.record(z.string(), z.record(z.string(), z.array(z.number().int().positive()))),
});

export const AnimeArtifactManifestSchema = z.object({
  schema_version: z.string(),
  generated_at: z.string(),
  metadata_count: z.number().int().nonnegative(),
  full_entry_count: z.number().int().nonnegative(),
  recommendation_source_count: z.number().int().nonnegative(),
  metadata_files: z.array(z.string()),
  full_files: z.array(z.string()),
  files: z.array(
    z.object({
      bytes: z.number().int().nonnegative(),
      path: z.string(),
      sha256: z.string(),
    }),
  ),
  search_metadata: z.string(),
  search_metadata_chunks: z.array(z.string()),
  build_identity: z.string(),
  provenance: z.record(z.string(), z.unknown()),
});

export type AnimeCardItem = z.infer<typeof AnimeCardItemSchema>;
export type AnimeImages = z.infer<typeof AnimeImagesSchema>;
export type AnimeCardMetadata = z.infer<typeof AnimeCardMetadataSchema>;
export type AnimeMetadata = AnimeCardMetadata;
export type AnimeEntry = z.infer<typeof AnimeEntrySchema>;
export type AnimeEntryChunk = z.infer<typeof AnimeEntryChunkSchema>;
export type AnimeMetadataChunk = z.infer<typeof AnimeMetadataChunkSchema>;
export type AnimeSearchMetadata = z.infer<typeof AnimeSearchMetadataSchema>;
export type AnimeSearchIndex = z.infer<typeof AnimeSearchIndexSchema>;
export type AnimeFilterIndex = z.infer<typeof AnimeFilterIndexSchema>;
export type AnimeArtifactManifest = z.infer<typeof AnimeArtifactManifestSchema>;
