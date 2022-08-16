import signal

class Killer:
    kill = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.incoming_signal)
        signal.signal(signal.SIGTERM, self.incoming_signal)
    
    def incoming_signal(self, *args):
        self.kill = True
    
    def exit_okay(self, code=0, message="received signal to exit, goodbye"):
        if self.kill:
            if message is not None:
                print(message)
            exit(code)
