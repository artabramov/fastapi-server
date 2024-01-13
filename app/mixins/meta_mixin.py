"""Meta mixin."""

class MetaMixin:
    """Mixin for classes that contain meta data."""

    def getmeta(self, meta_key: str):
        """Return meta value."""
        meta_list = [x for x in self.user_meta if x.meta_key == meta_key]
        if meta_list:
            return meta_list[0].meta_value
