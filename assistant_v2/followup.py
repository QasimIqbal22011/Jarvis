import time


class FollowUpManager:

    def __init__(self, timeout=8):

        self.timeout = timeout
        self.last_interaction = 0


    def start(self):

        self.last_interaction = time.time()


    def active(self):

        return (
            time.time() - self.last_interaction
        ) < self.timeout


    def reset(self):

        self.last_interaction = 0