# Rhyme analysis module - integrates Chinese, Japanese, Korean rhyme functions

# Import rhyme functions from original files
from .rhyme_chn import yayun, pingze, lvshi_yayun, fanti, has_heteronym
from .rhyme_jpn import jpn_yayun
from .rhyme_kor import kor_yayun

# Re-export all rhyme-related functions for unified management
__all__ = [
    'yayun',           # Chinese rhyme
    'pingze',          # Chinese tone pattern
    'lvshi_yayun',     # Chinese poetry rhyme
    'fanti',           # Chinese traditional
    'has_heteronym',   # Chinese multi-toned words
    'jpn_yayun',       # Japanese rhyme
    'kor_yayun'        # Korean rhyme
]
