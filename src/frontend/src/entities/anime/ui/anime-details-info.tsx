import type { AnimeDetailField } from '@/entities/anime/model/anime-details-model';

export interface AnimeDetailsInfoProps {
  details: AnimeDetailField[];
}

export function AnimeDetailsInfo({ details }: AnimeDetailsInfoProps) {
  return (
    <section aria-labelledby="anime-details-heading">
      <div>
        <h2 id="anime-details-heading" className="heading-h4">
          Details
        </h2>
        <dl className="mt-6 grid w-full gap-x-10 gap-y-6 sm:grid-cols-2 lg:gap-x-16">
          {details.map((detail) => (
            <DetailRow key={detail.label} {...detail} />
          ))}
        </dl>
      </div>
    </section>
  );
}

function DetailRow({ label, value }: AnimeDetailField) {
  return (
    <div className="grid gap-1">
      <dt className="text-sm font-semibold tracking-wide text-muted-foreground">{label}</dt>
      <dd className="body-copy text-foreground/90">{value}</dd>
    </div>
  );
}
