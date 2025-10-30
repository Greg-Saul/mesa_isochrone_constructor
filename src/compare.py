class compare:
    def __init__(self, figsize=(8, 12)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.models = None
        self.min_age_length = None
        self.ax.invert_xaxis()