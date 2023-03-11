"""Scryfall object models."""

import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from msgspec import Struct


class ScryColor(str, Enum):
    """Enum for https://scryfall.com/docs/api/colors#color-arrays"""

    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    TAP = "T"


class ScrySetType(str, Enum):
    """Enum for https://scryfall.com/docs/api/sets#set-types"""

    CORE = "core"
    EXPANSION = "expansion"
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
    TOKEN = "token"
    MEMORABILIA = "memorabilia"
    ALCHEMY = "alchemy"
    ARSENAL = "arsenal"
    MINIGAME = "minigame"


class ScryCardLayout(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#layout"""

    NORMAL = "normal"
    SPLIT = "split"
    FLIP = "flip"
    TRANSFORM = "transform"
    MODAL_DFC = "modal_dfc"
    MELD = "meld"
    LEVELER = "leveler"
    CLASS = "class"
    SAGA = "saga"
    ADVENTURE = "adventure"
    PLANAR = "planar"
    SCHEME = "scheme"
    VANGUARD = "vanguard"
    TOKEN = "token"
    DOUBLE_FACED_TOKEN = "double_faced_token"
    EMBLEM = "emblem"
    AUGMENT = "augment"
    HOST = "host"
    ART_SERIES = "art_series"
    DOUBLE_SIDED = "double_sided"
    REVERSIBLE_CARD = "reversible_card"


class ScryCardFrame(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#frames"""

    Y1993 = "1993"
    Y1997 = "1997"
    Y2003 = "2003"
    Y2015 = "2015"
    FUTURE = "future"


class ScryFrameEffect(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#frame-effects"""

    NONE = ""
    LEGENDARY = "legendary"
    MIRACLE = "miracle"
    NYXBORN = "nyxborn"
    NYXTOUCHED = "nyxtouched"
    DRAFT = "draft"
    DEVOID = "devoid"
    TOMBSTONE = "tombstone"
    COLORSHIFTED = "colorshifted"
    INVERTED = "inverted"
    SUNMOONDFC = "sunmoondfc"
    COMPASSLANDDFC = "compasslanddfc"
    ORIGINPWDFC = "originpwdfc"
    MOONELDRAZIDFC = "mooneldrazidfc"
    MOONREVERSEMOONDFC = "moonreversemoondfc"
    WAXINGANDWANINGMOONDFC = "waxingandwaningmoondfc"
    SHOWCASE = "showcase"
    EXTENDEDART = "extendedart"
    COMPANION = "companion"
    FULLART = "fullart"
    ETCHED = "etched"
    SNOW = "snow"
    LESSON = "lesson"
    TEXTLESS = "textless"
    SHATTEREDGLASS = "shatteredglass"
    CONVERTDFC = "convertdfc"
    FANDFC = "fandfc"
    UPSIDEDOWNDFC = "upsidedowndfc"
    GILDED = "gilded"


class ScryBorderColor(str, Enum):
    """Enum for card border_color"""

    BLACK = "black"
    BORDERLESS = "borderless"
    GOLD = "gold"
    SILVER = "silver"
    WHITE = "white"


class ScryFinish(str, Enum):
    """Enum for card finishes"""

    FOIL = "foil"
    NONFOIL = "nonfoil"
    ETCHED = "etched"
    GLOSSY = "glossy"


class ScryImageStatus(str, Enum):
    """Enum for card image_status"""

    MISSING = "missing"
    PLACEHOLDER = "placeholder"
    LOWRES = "lowres"
    HIGHRES_SCAN = "highres_scan"


class ScryGame(str, Enum):
    """Enum for card games"""

    PAPER = "paper"
    ARENA = "arena"
    MTGO = "mtgo"
    SEGA = "sega"
    ASTRAL = "astral"


class ScryRarity(str, Enum):
    """Enum for card rarity"""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"


class ScrySecurityStamp(str, Enum):
    """Enum for card security_stamp"""

    OVAL = "oval"
    TRIANGLE = "triangle"
    ACORN = "acorn"
    ARENA = "arena"
    CIRCLE = "circle"
    HEART = "heart"


class ScryFormat(str, Enum):
    """Enum for card legalities keys"""

    BRAWL = "brawl"
    COMMANDER = "commander"
    DUEL = "duel"
    FRONTIER = "frontier"
    FUTURE = "future"
    LEGACY = "legacy"
    MODERN = "modern"
    OLDSCHOOL = "oldschool"
    PAUPER = "pauper"
    PENNY = "penny"
    STANDARD = "standard"
    VINTAGE = "vintage"
    HISTORIC = "historic"
    PIONEER = "pioneer"
    GLADIATOR = "gladiator"
    EXPLORER = "explorer"
    HISTORICBRAWL = "historicbrawl"
    ALCHEMY = "alchemy"
    PAUPERCOMMANDER = "paupercommander"
    PREMODERN = "premodern"
    PREDH = "predh"


class ScryLegality(str, Enum):
    """Enum for card legalities values"""

    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    RESTRICTED = "restricted"
    BANNED = "banned"


class ScryMigrationStrategy(str, Enum):
    """Enum for migration strategy values"""

    MERGE = "merge"
    DELETE = "delete"


class ScrySet(
    Struct,
    tag_field="object",
    tag="set",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/sets"""

    id: UUID
    code: str
    mtgo_code: Optional[str] = None
    arena_code: Optional[str] = None
    tcgplayer_id: Optional[int] = None
    name: str
    set_type: ScrySetType
    released_at: Optional[dt.date] = None
    block_code: Optional[str] = None
    block: Optional[str] = None
    parent_set_code: Optional[str] = None
    card_count: int
    printed_size: Optional[int] = None
    digital: bool
    foil_only: bool
    nonfoil_only: Optional[bool] = None
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
    """Model for https://scryfall.com/docs/api/cards#related-card-objects"""

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
    """Model for https://scryfall.com/docs/api/cards#card-face-objects"""

    artist: Optional[str] = None
    artist_id: Optional[UUID] = None
    cmc: Optional[float] = None
    color_indicator: Optional[List[ScryColor]] = None
    colors: Optional[List[ScryColor]] = None
    flavor_name: Optional[str] = None
    flavor_text: Optional[str] = None
    illustration_id: Optional[UUID] = None
    image_uris: Optional[Dict[str, str]] = None
    layout: Optional[ScryCardLayout] = None
    loyalty: Optional[str] = None
    mana_cost: str
    name: str
    oracle_id: Optional[UUID] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    printed_name: Optional[str] = None
    printed_text: Optional[str] = None
    printed_type_line: Optional[str] = None
    toughness: Optional[str] = None
    type_line: Optional[str] = None
    watermark: Optional[str] = None


class CardPreviewBlock(Struct):
    """Model for card preview block."""

    source: str
    source_uri: Union[str, Literal[""], str]
    previewed_at: dt.date


class ScryCard(
    Struct,
    tag_field="object",
    tag="card",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/cards"""

    # Core Card Fields
    arena_id: Optional[int] = None
    id: UUID
    lang: str
    mtgo_id: Optional[int] = None
    mtgo_foil_id: Optional[int] = None
    multiverse_ids: Optional[List[int]] = None
    tcgplayer_id: Optional[int] = None
    tcgplayer_etched_id: Optional[int] = None
    cardmarket_id: Optional[int] = None
    oracle_id: Optional[UUID] = None
    prints_search_uri: str
    rulings_uri: str
    scryfall_uri: str
    uri: str
    # Gameplay Fields
    all_parts: Optional[List[ScryRelatedCard]] = None
    card_faces: Optional[List[ScryCardFace]] = None
    cmc: Optional[float] = None
    colors: Optional[List[ScryColor]] = None
    color_identity: List[ScryColor]
    color_indicator: Optional[List[ScryColor]] = None
    edhrec_rank: Optional[int] = None
    foil: bool
    hand_modifier: Optional[str] = None
    keywords: List[str]
    layout: ScryCardLayout
    legalities: Dict[ScryFormat, ScryLegality]
    life_modifier: Optional[str] = None
    loyalty: Optional[str] = None
    mana_cost: Optional[str] = None
    name: str
    nonfoil: bool
    oracle_text: Optional[str] = None
    oversized: bool
    penny_rank: Optional[int] = None
    power: Optional[str] = None
    produced_mana: Optional[List[str]] = None
    reserved: bool
    toughness: Optional[str] = None
    type_line: Optional[str] = None
    # Print Fields
    artist: Optional[str] = None
    artist_ids: Optional[List[UUID]] = None
    booster: bool
    border_color: ScryBorderColor
    card_back_id: Optional[UUID] = None
    collector_number: str
    content_warning: Optional[bool] = None
    digital: bool
    finishes: List[ScryFinish]
    flavor_name: Optional[str] = None
    flavor_text: Optional[str] = None
    frame_effect: Optional[ScryFrameEffect] = None
    frame_effects: Optional[List[ScryFrameEffect]] = None
    frame: ScryCardFrame
    full_art: bool
    games: List[ScryGame]
    highres_image: bool
    illustration_id: Optional[UUID] = None
    image_status: ScryImageStatus
    image_uris: Optional[Dict[str, str]] = None
    prices: Optional[Dict[str, Optional[Decimal]]]  # TODO: enum keys=None
    printed_name: Optional[str] = None
    printed_text: Optional[str] = None
    printed_type_line: Optional[str] = None
    promo: bool
    promo_types: Optional[List[str]] = None
    purchase_uris: Optional[Dict[str, str]] = None
    rarity: ScryRarity
    related_uris: Optional[Dict[str, str]] = None
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
    variation_of: Optional[UUID] = None
    security_stamp: Optional[ScrySecurityStamp] = None
    watermark: Optional[str] = None
    preview: Optional[CardPreviewBlock] = None


class ScryBulkData(
    Struct,
    tag_field="object",
    tag="bulk_data",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/bulk-data"""

    id: UUID
    uri: str
    type: str
    name: str
    description: str
    download_uri: str
    updated_at: dt.datetime
    compressed_size: Optional[int] = None
    content_type: str
    content_encoding: str


class ScryMigration(
    Struct,
    tag_field="object",
    tag="migration",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/migrations"""

    id: UUID
    uri: str
    performed_at: dt.date
    migration_strategy: ScryMigrationStrategy
    old_scryfall_id: UUID
    new_scryfall_id: Optional[UUID] = None
    note: Optional[str] = None


class ScryList(
    Struct,
    tag_field="object",
    tag="list",
    kw_only=True,
    omit_defaults=True,
):
    """Model for https://scryfall.com/docs/api/lists"""

    data: List[Union[ScrySet, ScryCard, ScryBulkData, ScryMigration]]
    has_more: bool
    next_page: Optional[str] = None
    total_cards: Optional[int] = None
    warnings: Optional[List[str]] = None
