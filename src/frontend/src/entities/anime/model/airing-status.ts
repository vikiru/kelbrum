export const AIRING_STATUSES = ['Currently Airing', 'Finished Airing', 'Not yet aired'] as const;

export type AiringStatus = (typeof AIRING_STATUSES)[number];

export const AIRING_STATUS_LABELS: Record<AiringStatus, string> = {
  'Currently Airing': 'Currently Airing',
  'Finished Airing': 'Finished Airing',
  'Not yet aired': 'Not yet aired',
};
