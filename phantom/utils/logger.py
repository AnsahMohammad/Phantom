import time
from .storage import Storage

class Logger:
    def __init__(self, show_logs=False, author=""):
        self.show_logs = show_logs
        self.logs = []
        self.author = author
        # Author format : Filename-Class eg: Storage-Database
        self.storage = Storage(table_name="errors")

    def log(self, content, origin="", **kwargs):
        log_ = f"{time.strftime('%H:%M:%S')} : "
        
        log_ += f"{self.author}-{origin} : "

        log_ += f"{content} | {kwargs}"

        self.logs.append(log_)
        if self.show_logs:
            print(log_)

    def error(self, content, origin=""):
        origin = self.author + "-" + origin
        self.log(content, origin, type="Error")
        self.storage.save_errors(content, origin)

    def save(self, filename="logs.txt"):
        with open(filename, "w") as f:
            for log in self.logs:
                f.write(log + "\n")
        self.log("Logs saved to logs.txt", "Log")
        self.logs.clear()
