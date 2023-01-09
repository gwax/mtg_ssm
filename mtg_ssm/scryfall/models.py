"""Scryfall object models."""

import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, HttpUrl
from pydantic.generics import GenericModel


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


T = TypeVar("T")


class ScryRootList(GenericModel, Generic[T]):
    """Model for unstructured list of scryfall objects (e.g. bulk file data)"""

    __root__: List[T]


class ScryObjectList(GenericModel, Generic[T]):
    """Model for https://scryfall.com/docs/api/lists"""

    object: Literal["list"] = "list"
    data: List[T]
    has_more: bool
    next_page: Optional[HttpUrl]
    total_cards: Optional[int]
    warnings: Optional[List[str]]


class ScrySet(BaseModel):
    """Model for https://scryfall.com/docs/api/sets"""

    object: Literal["set"] = "set"
    id: UUID
    code: str
    mtgo_code: Optional[str]
    arena_code: Optional[str]
    tcgplayer_id: Optional[int]
    name: str
    set_type: ScrySetType
    released_at: Optional[dt.date]
    block_code: Optional[str]
    block: Optional[str]
    parent_set_code: Optional[str]
    card_count: int
    printed_size: Optional[int]
    digital: bool
    foil_only: bool
    nonfoil_only: Optional[bool]
    icon_svg_uri: HttpUrl
    search_uri: HttpUrl
    scryfall_uri: HttpUrl
    uri: HttpUrl


class ScryRelatedCard(BaseModel):
    """Model for https://scryfall.com/docs/api/cards#related-card-objects"""

    object: Literal["related_card"] = "related_card"
    id: UUID
    component: str
    name: str
    type_line: str
    uri: HttpUrl


class ScryCardFace(BaseModel):
    """Model for https://scryfall.com/docs/api/cards#card-face-objects"""

    object: Literal["card_face"] = "card_face"
    artist: Optional[str]
    artist_id: Optional[UUID]
    cmc: Optional[Decimal]
    color_indicator: Optional[List[ScryColor]]
    colors: Optional[List[ScryColor]]
    flavor_name: Optional[str]
    flavor_text: Optional[str]
    illustration_id: Optional[UUID]
    image_uris: Optional[Dict[str, HttpUrl]]
    layout: Optional[ScryCardLayout]
    loyalty: Optional[str]
    mana_cost: str
    name: str
    oracle_id: Optional[UUID]
    oracle_text: Optional[str]
    power: Optional[str]
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    toughness: Optional[str]
    type_line: Optional[str]
    watermark: Optional[str]


class CardPreviewBlock(BaseModel):
    """Model for card preview block."""

    source: str
    source_uri: Union[HttpUrl, Literal[""], str]
    previewed_at: dt.date


class ScryCard(BaseModel):
    """Model for https://scryfall.com/docs/api/cards"""

    object: Literal["card"] = "card"
    # Core Card Fields
    arena_id: Optional[int]
    id: UUID
    lang: str
    mtgo_id: Optional[int]
    mtgo_foil_id: Optional[int]
    multiverse_ids: Optional[List[int]]
    tcgplayer_id: Optional[int]
    tcgplayer_etched_id: Optional[int]
    cardmarket_id: Optional[int]
    oracle_id: Optional[UUID]
    prints_search_uri: HttpUrl
    rulings_uri: HttpUrl
    scryfall_uri: HttpUrl
    uri: HttpUrl
    # Gameplay Fields
    all_parts: Optional[List[ScryRelatedCard]]
    card_faces: Optional[List[ScryCardFace]]
    cmc: Optional[Decimal]
    colors: Optional[List[ScryColor]]
    color_identity: List[ScryColor]
    color_indicator: Optional[List[ScryColor]]
    edhrec_rank: Optional[int]
    foil: bool
    hand_modifier: Optional[str]
    keywords: List[str]
    layout: ScryCardLayout
    legalities: Dict[ScryFormat, ScryLegality]
    life_modifier: Optional[str]
    loyalty: Optional[str]
    mana_cost: Optional[str]
    name: str
    nonfoil: bool
    oracle_text: Optional[str]
    oversized: bool
    penny_rank: Optional[int]
    power: Optional[str]
    produced_mana: Optional[List[Union[ScryColor, int]]]
    reserved: bool
    toughness: Optional[str]
    type_line: Optional[str]
    # Print Fields
    artist: Optional[str]
    artist_ids: Optional[List[UUID]]
    booster: bool
    border_color: ScryBorderColor
    card_back_id: Optional[UUID]
    collector_number: str
    content_warning: Optional[bool]
    digital: bool
    finishes: List[ScryFinish]
    flavor_name: Optional[str]
    flavor_text: Optional[str]
    frame_effect: Optional[ScryFrameEffect]
    frame_effects: Optional[List[ScryFrameEffect]]
    frame: ScryCardFrame
    full_art: bool
    games: List[ScryGame]
    highres_image: bool
    illustration_id: Optional[UUID]
    image_status: ScryImageStatus
    image_uris: Optional[Dict[str, HttpUrl]]
    prices: Optional[Dict[str, Optional[Decimal]]]  # TODO: enum keys
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    promo: bool
    promo_types: Optional[List[str]]
    purchase_uris: Optional[Dict[str, HttpUrl]]
    rarity: ScryRarity
    related_uris: Optional[Dict[str, HttpUrl]]
    released_at: dt.date
    reprint: bool
    scryfall_set_uri: HttpUrl
    set_name: str
    set_search_uri: HttpUrl
    set_type: str
    set_uri: HttpUrl
    set: str
    set_id: UUID
    story_spotlight: bool
    textless: bool
    variation: bool
    variation_of: Optional[UUID]
    security_stamp: Optional[ScrySecurityStamp]
    watermark: Optional[str]
    preview: Optional[CardPreviewBlock]


class ScryBulkData(BaseModel):
    """Model for https://scryfall.com/docs/api/bulk-data"""

    object: Literal["bulk_data"] = "bulk_data"
    id: UUID
    uri: HttpUrl
    type: str
    name: str
    description: str
    download_uri: HttpUrl
    updated_at: dt.datetime
    compressed_size: Optional[int]
    content_type: str
    content_encoding: str


class ScryMigration(BaseModel):
    """Model for https://scryfall.com/docs/api/migrations"""

    object: Literal["migration"] = "migration"
    id: UUID
    uri: HttpUrl
    performed_at: dt.date
    migration_strategy: ScryMigrationStrategy
    old_scryfall_id: UUID
    new_scryfall_id: Optional[UUID]
    note: Optional[str]
