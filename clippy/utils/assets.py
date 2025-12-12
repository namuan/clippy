import os
from .paths import MEDIA_ROOT, EXTRA_ROOT, ap

def load_icon(species):
    p1 = ap(os.path.join(EXTRA_ROOT, species, "icon.png"))
    if os.path.isfile(p1):
        return p1

    p2 = ap(os.path.join(MEDIA_ROOT, species, "icon.png"))
    if os.path.isfile(p2):
        return p2

    return None
