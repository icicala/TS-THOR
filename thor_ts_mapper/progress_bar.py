from tqdm import tqdm

class ProgressBar:
    _instance = None

    def __new__(cls, desc: str = "Progress"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, desc: str = "Progress"):
        if not self._initialized:
            self.desc = desc
            self.events_count = 0
            self.pbar = tqdm(unit=" event", desc=self.desc, dynamic_ncols=True)
            self._initialized = True
        elif desc != self.desc:
            self.pbar.set_description(desc)
            self.desc = desc

    def update(self, num: int = 1):
        self.events_count += num
        self.pbar.update(num)
        self.pbar.set_postfix({"processed": self.events_count})

    def close(self):
        if hasattr(self, 'pbar'):
            self.pbar.close()