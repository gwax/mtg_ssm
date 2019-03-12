"""Scryfall object models."""

from dataclasses import dataclass
import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import ClassVar
from typing import Dict
from typing import NewType
from typing import Optional
from typing import Sequence
from uuid import UUID

URI = NewType("URI", str)


class ScryObject:
    """Base object class for scryfall response objects."""

    object: ClassVar[str] = "object"


class ScryColor(str, Enum):
    """Enum for https://scryfall.com/docs/api/colors#color-arrays"""

    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"


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


class ScryCardLayout(str, Enum):
    """Enum for https://scryfall.com/docs/api/layouts#layout"""

    NORMAL = "normal"
    SPLIT = "split"
    FLIP = "flip"
    TRANSFORM = "transform"
    MELD = "meld"
    LEVELER = "leveler"
    SAGA = "saga"
    PLANAR = "planar"
    SCHEME = "scheme"
    VANGUARD = "vanguard"
    TOKEN = "token"
    DOUBLE_FACED_TOKEN = "double_faced_token"
    EMBLEM = "emblem"
    AUGMENT = "augment"
    HOST = "host"


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
    NYXTOUCHED = "nyxtouched"
    DRAFT = "draft"
    DEVOID = "devoid"
    TOMBSTONE = "tombstone"
    COLORSHIFTED = "colorshifted"
    SUNMOONDFC = "sunmoondfc"
    COMPASSLANDDFC = "compasslanddfc"
    ORIGINPWDFC = "originpwdfc"
    MOONELDRAZIDFC = "mooneldrazidfc"


class ScryBorderColor(str, Enum):
    """Enum for card border_color"""

    BLACK = "black"
    BORDERLESS = "borderless"
    GOLD = "gold"
    SILVER = "silver"
    WHITE = "white"


class ScryGame(str, Enum):
    """Enum for card games"""

    PAPER = "paper"
    ARENA = "arena"
    MTGO = "mtgo"


class ScryRarity(str, Enum):
    """Enum for card rarity"""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"


class ScryFormat(str, Enum):
    """Enum for card legalities keys"""

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


class ScryLegality(str, Enum):
    """Enum for card legalities values"""

    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    RESTRICTED = "restricted"
    BANNED = "banned"


@dataclass(frozen=True)
class ScryObjectList(ScryObject):
    """Model for https://scryfall.com/docs/api/lists"""

    object: ClassVar[str] = "list"
    data: Sequence[ScryObject]
    has_more: bool
    next_page: Optional[URI]
    total_cards: Optional[int]
    warnings: Optional[Sequence[str]]


@dataclass(frozen=True)
class ScrySet(ScryObject):
    """Model for https://scryfall.com/docs/api/sets"""

    object: ClassVar[str] = "set"
    id: UUID
    code: str
    mtgo_code: Optional[str]
    tcgplayer_id: Optional[int]
    name: str
    set_type: ScrySetType
    released_at: Optional[dt.date]
    block_code: Optional[str]
    block: Optional[str]
    parent_set_code: Optional[str]
    card_count: int
    digital: bool
    foil_only: bool
    icon_svg_uri: URI
    search_uri: URI
    scryfall_uri: URI
    uri: URI


@dataclass(frozen=True)
class ScryRelatedCard(ScryObject):
    """Model for https://scryfall.com/docs/api/cards#related-card-objects"""

    object: ClassVar[str] = "related_card"
    id: UUID
    component: str
    name: str
    type_line: str
    uri: URI


@dataclass(frozen=True)
class ScryCardFace(ScryObject):
    """Model for https://scryfall.com/docs/api/cards#card-face-objects"""

    object: ClassVar[str] = "card_face"
    artist: Optional[str]
    color_indicator: Optional[Sequence[ScryColor]]
    colors: Optional[Sequence[ScryColor]]
    flavor_text: Optional[str]
    illustration_id: Optional[UUID]
    image_uris: Optional[Dict[str, URI]]
    loyalty: Optional[str]
    mana_cost: str
    name: str
    oracle_text: Optional[str]
    power: Optional[str]
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    toughness: Optional[str]
    type_line: str
    watermark: Optional[str]


@dataclass(frozen=True)
class ScryCard(ScryObject):
    """Model for https://scryfall.com/docs/api/cards"""

    object: ClassVar[str] = "card"
    # Core Card Fields
    arena_id: Optional[int]
    id: UUID
    lang: str
    mtgo_id: Optional[int]
    mtgo_foil_id: Optional[int]
    multiverse_ids: Optional[Sequence[int]]
    tcgplayer_id: Optional[int]
    oracle_id: UUID
    prints_search_uri: URI
    rulings_uri: URI
    scryfall_uri: URI
    uri: URI
    # Gameplay Fields
    all_parts: Optional[Sequence[ScryRelatedCard]]
    card_faces: Optional[Sequence[ScryCardFace]]
    cmc: Decimal
    colors: Optional[Sequence[ScryColor]]
    color_identity: Sequence[ScryColor]
    color_indicator: Optional[Sequence[ScryColor]]
    edhrec_rank: Optional[int]
    foil: bool
    hand_modifier: Optional[str]
    layout: ScryCardLayout
    legalities: Dict[ScryFormat, ScryLegality]
    life_modifier: Optional[str]
    loyalty: Optional[str]
    mana_cost: Optional[str]
    name: str
    nonfoil: bool
    oracle_text: Optional[str]
    oversized: bool
    power: Optional[str]
    reserved: bool
    toughness: Optional[str]
    type_line: Optional[str]
    # Print Fields
    artist: Optional[str]
    border_color: ScryBorderColor
    collector_number: str
    digital: bool
    flavor_text: Optional[str]
    frame_effect: ScryFrameEffect
    frame: ScryCardFrame
    full_art: bool
    games: Sequence[ScryGame]
    highres_image: bool
    illustration_id: Optional[UUID]
    image_uris: Optional[Dict[str, URI]]
    prices: Optional[Dict[str, Decimal]]  # TODO: enum keys
    printed_name: Optional[str]
    printed_text: Optional[str]
    printed_type_line: Optional[str]
    promo: bool
    purchase_uris: Optional[Dict[str, URI]]
    rarity: ScryRarity
    related_uris: Optional[Dict[str, URI]]
    released_at: dt.date
    reprint: bool
    scryfall_set_uri: URI
    set_name: str
    set_search_uri: URI
    set_uri: URI
    set: str
    story_spotlight: bool
    watermark: Optional[str]


@dataclass(frozen=True)
class ScryBulkData(ScryObject):
    """Model for https://scryfall.com/docs/api/bulk-data"""

    object: ClassVar[str] = "bulk_data"
    id: UUID
    type: str
    name: str
    description: str
    permalink_uri: URI
    updated_at: dt.datetime
    size: Optional[int]
    compressed_size: Optional[int]
    content_type: str
    content_encoding: str
