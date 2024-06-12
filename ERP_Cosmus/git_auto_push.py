import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# to start - python auto_push.py
# to stop - echo. > shutdown.flag

class Watcher:
    DIRECTORY_TO_WATCH = "."
    SHUTDOWN_FILE = "shutdown.flag"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                if os.path.exists(self.SHUTDOWN_FILE):
                    print("Shutdown flag detected. Stopping the script.")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def process(event):
        if event.event_type == 'modified' and event.src_path.endswith("README.md"):
            try:
                subprocess.run(["git", "add", "README.md"], check=True)
                subprocess.run(["git", "commit", "-m", "Update README.md"], check=True)
                subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
                print("README.md changes pushed to the main branch.")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred: {e}")

    def on_modified(self, event):
        self.process(event)

if __name__ == '__main__':
    w = Watcher()
    w.run()