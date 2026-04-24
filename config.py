import sys

DEBUG_MODE = (
    "debugpy" in sys.modules or 
    "pydevd" in sys.modules or 
    sys.gettrace() is not None
)

WORLD_SEED = 82 

WIDTH, HEIGHT = 800, 600
PLANET_RADIUS = 2.0
SUN_RADIUS = 30.0     
ORBIT_RADIUS = 1500.0  
STAR_COUNT = 1500