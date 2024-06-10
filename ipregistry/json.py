from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union


class AsType(str, Enum):
    BUSINESS = 'business'
    EDUCATION = 'education'
    GOVERNMENT = 'government'
    HOSTING = 'hosting'
    INACTIVE = 'inactive'
    ISP = 'isp'


class RegionalInternetRegistry(str, Enum):
    AFRINIC = 'AFRINIC'
    APNIC = 'APNIC'
    ARIN = 'ARIN'
    JPNIC = 'JPNIC'
    KRNIC = 'KRNIC'
    LACNIC = 'LACNIC'
    RIPE_NCC = 'RIPE_NCC'
    TWNIC = 'TWNIC'


class AutonomousSystemPrefix(BaseModel):
    cidr: Optional[str] = None
    country_code: Optional[str] = None
    network_name: Optional[str] = None
    organization: Optional[str] = None
    prefix: Optional[str] = None
    registry: Optional[RegionalInternetRegistry] = None
    size: Optional[int] = None
    status: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class AutonomousSystemPrefixes(BaseModel):
    ipv4_count: Optional[int] = None
    ipv6_count: Optional[int] = None
    ipv4: Optional[List[AutonomousSystemPrefix]] = []
    ipv6: Optional[List[AutonomousSystemPrefix]] = []

    model_config = ConfigDict(extra='ignore')


class AutonomousSystemRelationships(BaseModel):
    downstreams: Optional[List[int]] = []
    peers: Optional[List[int]] = []
    upstreams: Optional[List[int]] = []

    model_config = ConfigDict(extra='ignore')


class AutonomousSystem(BaseModel):
    allocated: Optional[str] = None
    asn: Optional[int] = None
    country_code: Optional[str] = None
    domain: Optional[str] = None
    name: Optional[str] = None
    prefixes: Optional[AutonomousSystemPrefixes] = None
    relationships: Optional[AutonomousSystemRelationships] = None
    registry: Optional[RegionalInternetRegistry] = None
    type: Optional[AsType] = None
    updated: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Carrier(BaseModel):
    name: Optional[str] = None
    mcc: Optional[str] = None
    mnc: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Company(BaseModel):
    domain: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Connection(BaseModel):
    asn: Optional[int]
    domain: Optional[str]
    organization: Optional[str]
    route: Optional[str]
    type: Optional[str]

    model_config = ConfigDict(extra='ignore')


class CurrencyFormatPrefixSuffix(BaseModel):
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class CurrencyFormat(BaseModel):
    negative: CurrencyFormatPrefixSuffix
    positive: CurrencyFormatPrefixSuffix

    model_config = ConfigDict(extra='ignore')


class Currency(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    name_native: Optional[str] = None
    plural: Optional[str] = None
    plural_native: Optional[str] = None
    symbol: Optional[str] = None
    symbol_native: Optional[str] = None
    format: Optional[CurrencyFormat] = None

    model_config = ConfigDict(extra='ignore')


class Continent(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Flag(BaseModel):
    emoji: Optional[str] = None
    emoji_unicode: Optional[str] = None
    emojitwo: Optional[str] = None
    noto: Optional[str] = None
    twemoji: Optional[str] = None
    wikimedia: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Language(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    native: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Country(BaseModel):
    area: Optional[int] = None
    borders: Optional[List[str]] = []
    calling_code: Optional[str] = None
    capital: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    population: Optional[int] = None
    population_density: Optional[float] = None
    flag: Optional[Flag] = None
    languages: Optional[List[Language]] = []
    tld: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Region(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Location(BaseModel):
    continent: Optional[Continent] = None
    country: Optional[Country] = None
    region: Optional[Region] = None
    city: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language: Optional[Language] = None
    in_eu: Optional[bool] = None

    model_config = ConfigDict(extra='ignore')


class Security(BaseModel):
    is_abuser: Optional[bool] = None
    is_attacker: Optional[bool] = None
    is_bogon: Optional[bool] = None
    is_cloud_provider: Optional[bool] = None
    is_proxy: Optional[bool] = None
    is_relay: Optional[bool] = None
    is_tor: Optional[bool] = None
    is_tor_exit: Optional[bool] = None
    is_anonymous: Optional[bool] = None
    is_threat: Optional[bool] = None
    is_vpn: Optional[bool] = None

    model_config = ConfigDict(extra='ignore')


class TimeZone(BaseModel):
    id: Optional[str] = None
    abbreviation: Optional[str] = None
    current_time: Optional[str] = None
    name: Optional[str] = None
    offset: Optional[int] = None
    in_daylight_saving: Optional[bool] = None

    model_config = ConfigDict(extra='ignore')


class UserAgentDevice(BaseModel):
    brand: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class UserAgentEngine(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    version_major: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class UserAgentOperatingSystem(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class UserAgent(BaseModel):
    header: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    version_major: Optional[str] = None
    device: UserAgentDevice = None
    engine: UserAgentEngine = None
    os: UserAgentOperatingSystem = None

    model_config = ConfigDict(extra='ignore')


class IpInfo(BaseModel):
    ip: Optional[str] = None
    type: Optional[str] = None
    hostname: Optional[str] = None
    carrier: Optional[Carrier]  = None
    company: Optional[Company] = None
    connection: Optional[Connection] = None
    currency: Optional[Currency] = None
    location: Optional[Location] = None
    security: Optional[Security] = None
    time_zone: Optional[TimeZone] = None

    model_config = ConfigDict(extra='ignore')


class RequesterAutonomousSystem(AutonomousSystem):
    pass


class RequesterIpInfo(IpInfo):
    user_agent: Optional[UserAgent] = None

    model_config = ConfigDict(extra='ignore')