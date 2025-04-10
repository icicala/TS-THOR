from tqdm import tqdm


class ProgressBar:
    def __init__(self, desc="Progress", total=None, color="green", leave=True):
        self.events_count = 0

        bar_format = '[{elapsed}<{remaining}] {n_fmt}/{total_fmt} | {l_bar}{bar} {rate_fmt}{postfix}'

        self.pbar = tqdm(
            total=total,
            unit=" event",
            desc=desc,
            dynamic_ncols=True,
            position=0,
            leave=leave,
            bar_format=bar_format,
            colour=color
        )

    def update(self, num=1):
        self.events_count += num
        self.pbar.update(num)

    def close(self):
        if hasattr(self, 'pbar'):
            self.pbar.close()