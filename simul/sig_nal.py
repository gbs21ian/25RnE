import time

class SignalMap:
    def __init__(self, path):
        self.patterns = self.load_patterns(path)
        self.state = {}
        self.last_update = time.time()

    def load_patterns(self, path):
        patterns = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split(',')
                if len(parts)<4: continue
                r, c = int(parts[0]), int(parts[1])
                pattern_str, duration = parts[2], int(parts[3])
                patterns[(r,c)] = patterns.get((r,c), []) + [(pattern_str, duration)]
        return patterns

    def get_states(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        self.state = {}
        for rc, pat_seq in self.patterns.items():
            total = sum(p[1] for p in pat_seq)
            t = int(now) % total
            acc = 0
            for pstr, dur in pat_seq:
                if acc <= t < acc+dur:
                    dir_colors = {}
                    for dpart in pstr.split(';'):
                        dir, color = dpart.split('-')
                        dir_colors[dir] = color
                    self.state[rc] = dir_colors.get('N', 'red')
                    break
                acc += dur
        return self.state

    def get_state(self, rc):
        return self.get_states().get(rc, None)