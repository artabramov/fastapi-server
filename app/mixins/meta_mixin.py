class MetaMixin:
    def __getattr__(self, attr):
        if attr in self._meta_keys:
            return self._get_meta_value(attr)
        else:
            return self.__getattribute__(attr)

    def _get_meta_value(self, meta_key: str) -> str:
        return next(iter([x.meta_value for x in self.meta if x.meta_key == meta_key]), None)
