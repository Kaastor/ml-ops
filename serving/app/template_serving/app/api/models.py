from enum import Enum


class Stage(str, Enum):
    STAGING = 'Staging',
    PRODUCTION = 'Production',
    ARCHIVED = 'Archived'
