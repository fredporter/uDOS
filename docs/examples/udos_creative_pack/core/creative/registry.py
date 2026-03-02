from __future__ import annotations

from typing import Dict
from .writing.api import WritingAdapter
from .image.api import ImageAdapter
from .video.api import VideoAdapter
from .music.api import MusicAdapter
from .packaging.api import PackagingAdapter


def default_registry() -> Dict[str, object]:
    return {
        "writing": WritingAdapter(),
        "image": ImageAdapter(),
        "video": VideoAdapter(),
        "music": MusicAdapter(),
        "packaging": PackagingAdapter(),
    }
