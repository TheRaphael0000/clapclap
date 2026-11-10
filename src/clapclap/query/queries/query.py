

class Query:
    def save_to_playlist(self, name: str):
        raise NotImplementedError()

    def get_text(self):
        raise NotImplementedError()

    def get_json(self):
        raise NotImplementedError()
