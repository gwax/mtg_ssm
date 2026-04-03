"""Scryfall object models."""

import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import Generic, TypeAlias, TypeVar
from uuid import UUID

from msgspec import Struct


class ScryColor(str, Enum):
    """Enum for https://scryfall.com/docs/api/colors#color-arrays."""

    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    TAP = "T"


class ScrySetType(str, Enum):
    """Enum for https://scryfall.com/docs/api/sets#set-types."""

    CORE = "core"
    EXPANSION = "expansion"
    ETERNAL = "eternal"
    MASTERS = "masters"
    MASTERPIECE = "masterpiece"
    FROM_THE_VAULT = "from_the_vault"
    SPELLBOOK = "spellbook"
    PREMIUM_DECK = "premium_deck"
    DUEL_DECK = "duel_deck"
    DRAFT_INNOVATION = "draft_innovation"
    TREASURE_CHEST = "treasure_chest"
    COMMANDER = "commander"
    PLANECHASE = "planechase"
    ARCHENEMY = "archenemy"
    VANGUARD = "vanguard"
    FUNNY = "funny"
    STARTER = "starter"
    BOX = "box"
    PROMO = "promo"
    TOKEN = "token"  # noqa: S105
    MEMORABILIA = "memorabilia"
    ALCHEMY = "alchemy"
    ARSENAL = "arsenal"
    MINIGAME = "minigame"


class ScryCardLayout(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#layout."""

    ADVENTURE = "adventure"
    ART_SERIES = "art_series"
    AUGMENT = "augment"
    CASE = "case"
    CLASS = "class"
    DOUBLE_FACED_TOKEN = "double_faced_token"  # noqa: S105
    DOUBLE_SIDED = "double_sided"
    EMBLEM = "emblem"
    FLIP = "flip"
    HOST = "host"
    LEVELER = "leveler"
    MELD = "meld"
    MODAL_DFC = "modal_dfc"
    MUTATE = "mutate"
    NORMAL = "normal"
    PLANAR = "planar"
    PROTOTYPE = "prototype"
    REVERSIBLE_CARD = "reversible_card"
    SAGA = "saga"
    SCHEME = "scheme"
    SPLIT = "split"
    TOKEN = "token"  # noqa: S105
    TRANSFORM = "transform"
    VANGUARD = "vanguard"


class ScryCardFrame(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#frames."""

    Y1993 = "1993"
    Y1997 = "1997"
    Y2003 = "2003"
    Y2015 = "2015"
    FUTURE = "future"


class ScryFrameEffect(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#frame-effects."""

    NONE = ""

    BORDERLESS = "borderless"
    COLORSHIFTED = "colorshifted"
    COMPANION = "companion"
    COMPASSLANDDFC = "compasslanddfc"
    CONVERTDFC = "convertdfc"
    DEVOID = "devoid"
    DRAFT = "draft"
    ENCHANTMENT = "enchantment"
    ETCHED = "etched"
    EXTENDEDART = "extendedart"
    FANDFC = "fandfc"
    FULLART = "fullart"
    GILDED = "gilded"
    GRAVESTONE = "gravestone"
    INVERTED = "inverted"
    LEGENDARY = "legendary"
    LESSON = "lesson"
    MIRACLE = "miracle"
    MOONELDRAZIDFC = "mooneldrazidfc"
    MOONREVERSEMOONDFC = "moonreversemoondfc"
    NYXBORN = "nyxborn"
    NYXTOUCHED = "nyxtouched"
    ORIGINPWDFC = "originpwdfc"
    PROMO = "promo"
    SHATTEREDGLASS = "shatteredglass"
    SHOWCASE = "showcase"
    SNOW = "snow"
    SPREE = "spree"
    STAMPED = "stamped"
    SUNMOONDFC = "sunmoondfc"
    TEXTLESS = "textless"
    THICK = "thick"
    TOMBSTONE = "tombstone"
    TRANSLUCENT = "translucent"
    UPSIDEDOWNDFC = "upsidedowndfc"
    VEHICLE = "vehicle"
    WAXINGANDWANINGMOONDFC = "waxingandwaningmoondfc"


class ScryBorderColor(str, Enum):
    """Enum for card border_color."""

    BLACK = "black"
    BORDERLESS = "borderless"
    GOLD = "gold"
    SILVER = "silver"
    WHITE = "white"
    YELLOW = "yellow"


class ScryFinish(str, Enum):
    """Enum for card finishes."""

    FOIL = "foil"
    NONFOIL = "nonfoil"
    ETCHED = "etched"
    GLOSSY = "glossy"


class ScryImageStatus(str, Enum):
    """Enum for card image_status."""

    MISSING = "missing"
    PLACEHOLDER = "placeholder"
    LOWRES = "lowres"
    HIGHRES_SCAN = "highres_scan"


class ScryGame(str, Enum):
    """Enum for card games."""

    PAPER = "paper"
    ARENA = "arena"
    MTGO = "mtgo"
    SEGA = "sega"
    ASTRAL = "astral"


class ScryRarity(str, Enum):
    """Enum for card rarity."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"


class ScrySecurityStamp(str, Enum):
    """Enum for card security_stamp."""

    OVAL = "oval"
    TRIANGLE = "triangle"
    ACORN = "acorn"
    ARENA = "arena"
    CIRCLE = "circle"
    HEART = "heart"


class ScryFormat(str, Enum):
    """Enum for card legalities keys."""

    ALCHEMY = "alchemy"
    BRAWL = "brawl"
    COMMANDER = "commander"
    DUEL = "duel"
    EXPLORER = "explorer"
    FRONTIER = "frontier"
    FUTURE = "future"
    GLADIATOR = "gladiator"
    HISTORIC = "historic"
    HISTORICBRAWL = "historicbrawl"
    LEGACY = "legacy"
    MODERN = "modern"
    OATHBREAKER = "oathbreaker"
    OLDSCHOOL = "oldschool"
    PAUPER = "pauper"
    PAUPERCOMMANDER = "paupercommander"
    PENNY = "penny"
    PIONEER = "pioneer"
    PREDH = "predh"
    PREMODERN = "premodern"
    STANDARD = "standard"
    STANDARDBRAWL = "standardbrawl"
    TIMELESS = "timeless"
    VINTAGE = "vintage"


class ScryLegality(str, Enum):
    """Enum for card legalities values."""

    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    RESTRICTED = "restricted"
    BANNED = "banned"


class ScryMigrationStrategy(str, Enum):
    """Enum for migration strategy values."""

    MERGE = "merge"
    DELETE = "delete"


class ScrySet(
    Struct,
    tag_field="object",
    tag="set",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/sets."""

    id: UUID
    code: str
    mtgo_code: str | None = None
    arena_code: str | None = None
    tcgplayer_id: int | None = None
    name: str
    set_type: ScrySetType
    released_at: dt.date | None = None
    block_code: str | None = None
    block: str | None = None
    parent_set_code: str | None = None
    card_count: int
    printed_size: int | None = None
    digital: bool
    foil_only: bool
    nonfoil_only: bool | None = None
    icon_svg_uri: str
    search_uri: str
    scryfall_uri: str
    uri: str


class ScryRelatedCard(
    Struct,
    tag_field="object",
    tag="related_card",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/cards#related-card-objects."""

    id: UUID
    component: str
    name: str
    type_line: str
    uri: str


class ScryCardFace(
    Struct,
    tag_field="object",
    tag="card_face",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/cards#card-face-objects."""

    artist: str | None = None
    artist_id: UUID | None = None
    cmc: float | None = None
    color_indicator: list[ScryColor] | None = None
    colors: list[ScryColor] | None = None
    flavor_name: str | None = None
    flavor_text: str | None = None
    illustration_id: UUID | None = None
    image_uris: dict[str, str] | None = None
    layout: ScryCardLayout | None = None
    loyalty: str | None = None
    mana_cost: str
    name: str
    oracle_id: UUID | None = None
    oracle_text: str | None = None
    power: str | None = None
    printed_name: str | None = None
    printed_text: str | None = None
    printed_type_line: str | None = None
    toughness: str | None = None
    type_line: str | None = None
    watermark: str | None = None


class CardPreviewBlock(Struct):
    """Model for card preview block."""

    source: str
    source_uri: str
    previewed_at: dt.date


class ScryCard(
    Struct,
    tag_field="object",
    tag="card",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/cards."""

    # Core Card Fields
    arena_id: int | None = None
    id: UUID
    lang: str
    mtgo_id: int | None = None
    mtgo_foil_id: int | None = None
    multiverse_ids: list[int] | None = None
    tcgplayer_id: int | None = None
    tcgplayer_etched_id: int | None = None
    cardmarket_id: int | None = None
    oracle_id: UUID | None = None
    prints_search_uri: str
    rulings_uri: str
    scryfall_uri: str
    uri: str
    # Gameplay Fields
    all_parts: list[ScryRelatedCard] | None = None
    card_faces: list[ScryCardFace] | None = None
    cmc: float | None = None
    colors: list[ScryColor] | None = None
    color_identity: list[ScryColor]
    color_indicator: list[ScryColor] | None = None
    edhrec_rank: int | None = None
    foil: bool
    hand_modifier: str | None = None
    keywords: list[str]
    layout: ScryCardLayout
    legalities: dict[ScryFormat, ScryLegality]
    life_modifier: str | None = None
    loyalty: str | None = None
    mana_cost: str | None = None
    name: str
    nonfoil: bool
    oracle_text: str | None = None
    oversized: bool
    penny_rank: int | None = None
    power: str | None = None
    produced_mana: list[str] | None = None
    reserved: bool
    toughness: str | None = None
    type_line: str | None = None
    # Print Fields
    artist: str | None = None
    artist_ids: list[UUID] | None = None
    booster: bool
    border_color: ScryBorderColor
    card_back_id: UUID | None = None
    collector_number: str
    content_warning: bool | None = None
    digital: bool
    finishes: list[ScryFinish]
    flavor_name: str | None = None
    flavor_text: str | None = None
    frame_effect: ScryFrameEffect | None = None
    frame_effects: list[ScryFrameEffect] | None = None
    frame: ScryCardFrame
    full_art: bool
    games: list[ScryGame]
    highres_image: bool
    illustration_id: UUID | None = None
    image_status: ScryImageStatus
    image_uris: dict[str, str] | None = None
    prices: dict[str, Decimal | None] | None  # TODO: enum keys=None
    printed_name: str | None = None
    printed_text: str | None = None
    printed_type_line: str | None = None
    promo: bool
    promo_types: list[str] | None = None
    purchase_uris: dict[str, str] | None = None
    rarity: ScryRarity
    related_uris: dict[str, str] | None = None
    released_at: dt.date
    reprint: bool
    scryfall_set_uri: str
    set_name: str
    set_search_uri: str
    set_type: str
    set_uri: str
    set: str
    set_id: UUID
    story_spotlight: bool
    textless: bool
    variation: bool
    variation_of: UUID | None = None
    security_stamp: ScrySecurityStamp | None = None
    watermark: str | None = None
    preview: CardPreviewBlock | None = None


class ScryBulkData(
    Struct,
    tag_field="object",
    tag="bulk_data",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/bulk-data."""

    id: UUID
    uri: str
    type: str
    name: str
    description: str
    download_uri: str
    updated_at: dt.datetime
    compressed_size: int | None = None
    content_type: str
    content_encoding: str


class ScryMigration(
    Struct,
    tag_field="object",
    tag="migration",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/migrations."""

    id: UUID
    uri: str
    performed_at: dt.date
    migration_strategy: ScryMigrationStrategy
    old_scryfall_id: UUID
    new_scryfall_id: UUID | None = None
    note: str | None = None


ScryListable: TypeAlias = ScryBulkData | ScryCard | ScryMigration | ScrySet

_ScryListableT = TypeVar("_ScryListableT", bound=ScryListable)


class ScryList(
    Struct,
    Generic[_ScryListableT],
    tag_field="object",
    tag="list",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/lists."""

    data: list[_ScryListableT]
    has_more: bool
    next_page: str | None = None
    total_cards: int | None = None
    warnings: list[str] | None = None
