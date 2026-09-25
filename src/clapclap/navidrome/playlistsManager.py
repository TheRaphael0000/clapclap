import json

from clapclap.navidrome.navidrome import Navidrome
from clapclap.utils.log import logger

class PlaylistsManager:
    def __init__(self, regex, delete, stats):
        self.navidrome = Navidrome()
        self.regex = regex
        self.delete = delete
        self.stats = stats

    def run(self):
        playlists = self.navidrome.get_playlists_regex(self.regex)

        for playlist in playlists:
            id, name = playlist["id"], playlist["name"]

            if self.delete:
                self.navidrome.delete_playlist(id=id)
                print(name)
            elif self.stats:
                stats = self.navidrome.get_playlist_stats(id=id)
                print(json.dumps(stats))
            else:
                print(name)

        if self.delete:
            print(f"{len(playlists)} playlist(s) deleted")
        elif not self.stats:
            print(f"{len(playlists)} playlist(s) selected")