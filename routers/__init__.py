from .site import router as site
from .well import router as well
from .team import router as team
from .intervention import router as intervention
from .production import router as production
from .incident import router as incident
from .dashboard import router as dasboard

__all__ = ["site", "well", "team", "intervention", "production", "incident","dasboard"]
