import os
import time
import urllib.error
import urllib.request

from graceful_exit import Killer


GRINDSTONE_DB = os.environ["GRINDSTONE_DB"]
SERVER_URL = os.environ["SERVER_URL"] + "?token=" + os.environ["TOKEN"]
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", "30"))


def upload_db(server, content):
    req = urllib.request.Request(
        server,
        data=content.encode("utf-8"),
        headers={
            "content-type": "application/json"
        }
    )
    urllib.request.urlopen(req)


def main():
    killer = Killer()
    while True:
        killer.exit_okay()

        try:
            with open(GRINDSTONE_DB, encoding="utf-8") as f:
                print("reading grindstone database")
                db_content = f.read()
            print("uploading database")
            upload_db(SERVER_URL, db_content)
        except FileNotFoundError:
            print(f"error: database file '{GRINDSTONE_DB}' not found")
        except urllib.error.URLError:
            print(f"error: server '{SERVER_URL}' not reachable")
        except ConnectionResetError:
            print(f"error: connection to '{SERVER_URL}' reset")
        
        print(f"done, sleeping for {SLEEP_TIME}s")

        for _ in range(SLEEP_TIME):
            killer.exit_okay()
            time.sleep(1)



if __name__ == "__main__":
    main()
