from pprint import pprint

from app.gmgn_client import trending

data = trending(3)

print("SUCCESS")
print()

pprint(data["data"]["rank"][0])
