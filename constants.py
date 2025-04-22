import os

# Websites to crawl hero descriptions
DOTA2_URL = "https://dota2.fandom.com"

# Apis to crawl hero stats
HEROES_URL = "https://api.opendota.com/api/heroes"
BENCHMARK_BY_HERO_ID_URL = "https://api.opendota.com/api/benchmarks" # ?hero_id=1
HEROES_STATS_URL = "https://api.opendota.com/api/heroStats"
CLOUDFLARE_OPEN_DOTA_URL = "https://cdn.cloudflare.steamstatic.com"

# HTTP client constants
MAX_RETRY_COUNT = 5
RATE_LIMIT_STATUS_CODE = 429

# Courses Service Url
COURSE_SERVICE_URL = os.environ.get("COURSE_SERVICE_URL", "http://host.docker.internal:8002")