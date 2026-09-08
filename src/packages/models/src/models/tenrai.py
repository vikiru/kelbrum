"""Typed projections of the Tenrai catalogue response."""

import msgspec


class Taxonomy(msgspec.Struct, frozen=True):
    mal_id: int
    name: str
    type: str | None = None
    url: str | None = None


class NamedResource(msgspec.Struct, frozen=True):
    mal_id: int
    name: str
    type: str | None = None
    url: str | None = None


class DateParts(msgspec.Struct, frozen=True):
    day: int | None = None
    month: int | None = None
    year: int | None = None


class Aired(msgspec.Struct, frozen=True):
    from_: str | None = msgspec.field(name='from', default=None)
    to: str | None = None
    prop: 'AiredProperties' = msgspec.field(default_factory=lambda: AiredProperties())
    string: str | None = None


class AiredProperties(msgspec.Struct, frozen=True):
    from_: DateParts = msgspec.field(name='from', default_factory=DateParts)
    to: DateParts = msgspec.field(default_factory=DateParts)


class Broadcast(msgspec.Struct, frozen=True):
    day: str | None = None
    time: str | None = None
    timezone: str | None = None
    string: str | None = None


class ImageVariant(msgspec.Struct, frozen=True):
    image_url: str | None = None
    small_image_url: str | None = None
    large_image_url: str | None = None


class TrailerImages(msgspec.Struct, frozen=True):
    image_url: str | None = None
    small_image_url: str | None = None
    medium_image_url: str | None = None
    large_image_url: str | None = None
    maximum_image_url: str | None = None


class Images(msgspec.Struct, frozen=True):
    jpg: ImageVariant | None = None
    webp: ImageVariant | None = None


class Trailer(msgspec.Struct, frozen=True):
    url: str | None = None
    youtube_id: str | None = None
    embed_url: str | None = None
    images: TrailerImages | None = None
    title: str | None = None
    views: int | None = None
    likes: int | None = None
    dislikes: int | None = None
    comment_count: int | None = None
    published_at: str | None = None
    duration: str | None = None
    privacy_status: str | None = None
    region_restriction: 'RegionRestriction | None' = None
    embeddable: bool | None = None


class RegionRestriction(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    allowed: tuple[str, ...] = ()
    blocked: tuple[str, ...] = ()


class ExternalLink(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    name: str
    url: str


class StreamingLink(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    name: str
    url: str


class ThemeSongs(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    openings: list[str] = msgspec.field(default_factory=list)
    endings: list[str] = msgspec.field(default_factory=list)


class RelationEntry(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    """Anime-side relation target returned by full-detail responses."""

    mal_id: int
    type: str | None = None
    name: str | None = None
    url: str | None = None
    media_type: str | None = None


class AnimeRelation(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    """Named relation group returned by the full anime endpoint."""

    relation: str
    entry: list[RelationEntry] = msgspec.field(default_factory=list)


class TitleVariant(msgspec.Struct, frozen=True):
    type: str
    title: str


class TenraiAnimeEntry(msgspec.Struct, frozen=True, forbid_unknown_fields=False):
    mal_id: int
    title: str
    titles: list[TitleVariant] = msgspec.field(default_factory=list)
    url: str | None = None
    approved: bool | None = None
    title_english: str | None = None
    title_japanese: str | None = None
    title_synonyms: list[str] = msgspec.field(default_factory=list)
    type: str | None = None
    source: str | None = None
    episodes: int | None = None
    duration: str | None = None
    status: str | None = None
    airing: bool | None = None
    year: int | None = None
    aired: Aired | None = None
    broadcast: Broadcast | None = None
    rating: str | None = None
    season: str | None = None
    score: float | None = None
    scored_by: int | None = None
    rank: int | None = None
    popularity: int | None = None
    members: int | None = None
    favorites: int | None = None
    synopsis: str | None = None
    background: str | None = None
    moreinfo: str | None = None
    images: Images | None = None
    trailer: Trailer | None = None
    external: list[ExternalLink] = msgspec.field(default_factory=list)
    streaming: list[StreamingLink] = msgspec.field(default_factory=list)
    theme: ThemeSongs | None = None
    producers: list[NamedResource] = msgspec.field(default_factory=list)
    licensors: list[NamedResource] = msgspec.field(default_factory=list)
    studios: list[NamedResource] = msgspec.field(default_factory=list)
    genres: list[Taxonomy] = msgspec.field(default_factory=list)
    explicit_genres: list[Taxonomy] = msgspec.field(default_factory=list)
    themes: list[Taxonomy] = msgspec.field(default_factory=list)
    demographics: list[Taxonomy] = msgspec.field(default_factory=list)
    relations: list[AnimeRelation] = msgspec.field(default_factory=list)


class Pagination(msgspec.Struct, frozen=True):
    last_visible_page: int = 1
    has_next_page: bool = False
    current_page: int = 1
    items: 'PaginationItems | None' = None


class PaginationItems(msgspec.Struct, frozen=True):
    count: int = 0
    total: int = 0
    per_page: int = 0


class TenraiListResponse[EntryT](msgspec.Struct, frozen=True):
    data: list[EntryT]
    pagination: Pagination | None = None


class TenraiObjectResponse[EntryT](msgspec.Struct, frozen=True):
    data: EntryT


class CanonicalAnime(msgspec.Struct, frozen=True):
    mal_id: int
    url: str | None
    title: str
    title_english: str | None
    title_japanese: str | None
    title_synonyms: tuple[str, ...]
    anime_type: str | None
    source: str | None
    rating: str | None
    season: str | None
    episodes: int | None
    duration_minutes: int | None
    year: int | None
    status: str | None
    score: float | None
    synopsis: str | None
    synopsis_features: str | None
    background: str | None
    moreinfo: str | None
    images: Images | None
    trailer: Trailer | None
    external: tuple[ExternalLink, ...]
    streaming: tuple[StreamingLink, ...]
    theme: ThemeSongs | None
    studios: tuple[NamedResource, ...]
    producers: tuple[NamedResource, ...]
    licensors: tuple[NamedResource, ...]
    genres: tuple[Taxonomy, ...]
    themes: tuple[Taxonomy, ...]
    demographics: tuple[Taxonomy, ...]
    relations: tuple[AnimeRelation, ...]
