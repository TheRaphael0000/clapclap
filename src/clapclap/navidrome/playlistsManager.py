import re
import logging

from clapclap.navidrome.navidrome import Navidrome
logger = logging.getLogger("METADATA")

class PlaylistsManager:
    def __init__(self, regex, delete):
        self.navidrome = Navidrome()
        self.regex = regex
        self.delete = delete


    def run(self):
        response = self.navidrome.get_playlists()

        is_list = not self.regex and not self.delete
        count = 0

        for playlist in response["playlists"]["playlist"]:
            id, name = playlist["id"], playlist["name"]

            if is_list:
                print(name)
                count += 1
            else:
                match = re.match(string=name, pattern=self.regex)

                if self.delete and match is not None:
                    self.navidrome.delete_playlist(id=id)
                    print(name)
                    count += 1
                elif self.regex and match is not None:
                    print(name)
                    count += 1

        if is_list:
            print(f"{count} playlist(s)")
        elif self.delete:
            print(f"{count} playlist(s) deleted")
        elif self.regex:
            print(f"{count} playlist(s) selected")