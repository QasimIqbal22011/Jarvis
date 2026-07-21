class EventBus:

    def __init__(self):
        self.listeners = []


    def subscribe(self, callback):

        self.listeners.append(callback)


    def emit(self, event, data=None):

        for callback in self.listeners:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Event error: {e}")