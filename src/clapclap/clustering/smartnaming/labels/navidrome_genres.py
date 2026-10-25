def get_navidrome_genres(min_count=10):
    from clapclap.navidrome.navidrome import Navidrome
    navidrome = Navidrome()
    navidrome_genres = navidrome.get_genres()
    genres = [g["value"] for g in navidrome_genres["genres"]
              ["genre"] if g["songCount"] > min_count]
    return set(genres)
