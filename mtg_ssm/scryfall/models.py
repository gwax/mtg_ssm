"""Scryfall object models."""

import datetime as dt
from enum import Enum
from uuid import UUID

from typing import Any, Dict, List, NamedTuple, NewType, Optional


URI = NewType('URI', str)


class ScryfallColor(str, Enum):
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'


class ScryfallList(NamedTuple):
    has_more: bool
    data: List[Any]
    next_page: Optional[URI]
    total_cards: Optional[int]
    warnings: Optional[List[str]]


class ScryfallBulkData(NamedTuple):
    id_: UUID
    type_: str
    name: str
    description: str
    permalink_uri: URI
    updated_at: dt.datetime
    size: Optional[int]
    compressed_size: Optional[int]
    content_type: str
    content_encoding: str


class ScryfallRelatedCard(NamedTuple):
    id_: UUID
    name: str
    uri: URI


class ScryfallCardFace(NamedTuple):
    color_indicator: Optional[List[ScryfallColor]]
    colors: Optional[List[ScryfallColor]]
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


class ScryfallCard(NamedTuple):
    # Core fields
    arena_id: Optional[int]
    id_: UUID
    lang: str
    mtgo_id: Optional[int]
    mtgo_foil_id: Optional[int]
    multiverse_ids: Optional[List[int]]
    oracle_id: UUID
    prints_search_uri: URI
    rulings_uri: URI
    scryfall_uri: URI
    uri: URI

    # Gameplay fields
    all_parts: Optional[List[ScryfallRelatedCard]]
    card_faces: Optional[List[ScryfallCardFace]]
    cmc: float
    colors: Optional[List[ScryfallColor]]
    color_identity: List[ScryfallColor]
    color_indicator: Optional[List[ScryfallColor]]
    edhrec_rank: Optional[int]
    foil: bool
    hand_modifier: Optional[str]
    layout: str
    legalities: Dict[str, str]
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

    # Print fields
    artist: Optional[str]
    border_color: str
    collector_number: str
    colorshifted: bool
    digital: bool
    eur: Optional[str]
    flavor_text: Optional[str]
    frame: str
    full_art: bool
    futureshifted: bool

    highres_image: bool
    illustration_id: Optional[UUID]
    image_uris: Optional[Dict[str, URI]]
    purchase_uris: Optional[Dict[str, URI]]
    rarity: str
    related_uris: Optional[Dict[str, URI]]
    reprint: bool
    scryfall_set_uri: URI
    set_: str
    set_name: str
    set_search_uri: URI
    set_uri: URI
    story_spotlight_number: Optional[int]
    story_spotlight_uri: Optional[URI]
    timeshifted: bool
    tix: Optional[str]
    usd: Optional[str]
    watermark: Optional[str]


class ScryfallSetType(str, Enum):
    CORE = 'core'
    EXPANSION = 'expansion'
    MASTERS = 'masters'
    MASTERPIECE = 'masterpiece'
    FROM_THE_VAULT = 'from_the_vault'
    SPELLBOOK = 'spellbook'
    PREMIUM_DECK = 'premium_deck'
    DUEL_DECK = 'duel_deck'
    DRAFT_INNOVATION = 'draft_innovation'
    COMMANDER = 'commander'
    PLANECHASE = 'planechase'
    ARCHENEMY = 'archenemy'
    VANGUARD = 'vanguard'
    FUNNY = 'funny'
    STARTER = 'starter'
    BOX = 'box'
    PROMO = 'promo'
    TOKEN = 'token'
    MEMORABILIA = 'memorabilia'
    TREASURE_CHEST = 'treasure_chest'


class ScryfallSet(NamedTuple):
    code: str
    mtgo_code: Optional[str]
    name: str
    uri: URI
    set_type: ScryfallSetType
    released_at: Optional[dt.date]
    block_code: Optional[str]
    block: Optional[str]
    parent_set_code: Optional[str]
    card_count: int
    digital: bool
    foil_only: bool
    icon_svg_uri: URI
    search_uri: URI
