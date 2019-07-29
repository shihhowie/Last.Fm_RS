import pylast
import pandas as pd

API_KEY = "92e5065a366659b3cb6940ae714bb41f"
API_SECRET = "9b95e86fe7e4ff114cb2622889f1e37e"
username = "thehowieman"

password_hash = pylast.md5("h#11122")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)


sams_profile = network.get_user("BegGsAnator")
print(sams_profile.get_info())