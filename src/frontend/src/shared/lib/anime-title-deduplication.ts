export function deduplicateAnimeTitles(values: readonly (string | null | undefined)[]): string[] {
  const seen = new Set<string>();

  return values.flatMap((value) => {
    const normalizedValue = value?.trim();
    if (!normalizedValue) return [];

    const key = normalizedValue.toLocaleLowerCase();
    if (seen.has(key)) return [];

    seen.add(key);
    return [normalizedValue];
  });
}
