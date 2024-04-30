import time


class Logger:
    def __init__(self, show_logs=False):
        self.show_logs = show_logs
        self.logs = []

    def log(self, content, id=None, **kwargs):
        log_ = f"{time.strftime('%H:%M:%S')} : "
        if id:
            log_ += f"{id} : "

        log_ += f"{content} | {kwargs}"

        self.logs.append(log_)
        if self.show_logs:
            print(log_)

    def save(self, filename="logs.txt"):
        with open(filename, "w") as f:
            for log in self.logs:
                f.write(log + "\n")
        self.log("Logs saved to logs.txt", "Log")
        self.logs.clear()
