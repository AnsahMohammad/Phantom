import os
from supabase import create_client
import json

# from ..utils.logger import Logger


class Storage:
    def __init__(self, table_name="index", resume=False, remote_db=True):
        self.table_name = table_name
        self.data = {}

        self.resume = resume
        self.remote_db = remote_db

        # remote client set-up
        self.url = os.environ.get("SUPABASE_URL", None)
        self.key = os.environ.get("SUPABASE_KEY", None)
        try:
            self.supabase = create_client(self.url, self.key)
            if not self.supabase:
                print("Failed to connect to Supabase")
                self.remote_db = False
        except Exception as e:
            print(f"Error while creating Supabase client: {e}")
            self.remote_db = False

        self.log_errors = os.environ.get("LOG_ERRORS", False)

        print("Remote database : ", self.remote_db)
        print("DB Ready")

    def add(self, key, value, title=None):
        # TODO: Genaralize the function to accept any table name
        if self.remote_db:
            try:
                data, count = (
                    self.supabase.table(self.table_name)
                    .insert({"url": key, "content": value, "title": title})
                    .execute()
                )
            except Exception as e:
                print(f"\nError inserting record into {self.table_name} table: {e}\n")
                return False
            return True

        # print("value is of length : ", len(value))
        self.data[key] = value
        return True

    def fetch_visited(self):
        visited = set()
        if self.resume and self.remote_db:
            # if resume the execution and remote db available
            response = self.supabase.table("index").select("url").execute()
            for row in response["data"]:
                visited.add(row["url"])
            print("Visited URLs fetched from remote DB : ", len(visited))

        return visited

    def save_errors(self, errors, origin=None):
        if not self.log_errors:
            return
        if self.remote_db:
            try:
                data, count = (
                    self.supabase.table("errors").insert({"error": errors}).execute()
                )
            except Exception as e:
                print(f"\nError inserting record into errors table: {e}\n")
                return False
            return True

        with open("errors.json", "a") as f:
            json.dump(errors, f)
        return True

    def save(self):
        if self.remote_db:
            return
        table_name = self.table_name + ".json"
        with open(table_name, "w") as f:
            json.dump(self.data, f)


class Database:
    def __init__(self):
        self.state = True
        showlogs = os.environ.get("SHOW_LOGS", "1") == "1"
        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))
        self.CHUNK_LIMIT = int(os.environ.get("CHUNK_LIMIT", 5000))
        self.state = self.check_remote()
        print("DB Initialized : ", self.state)

    def check_remote(self):
        remote_db = True

        self.db_url = os.environ.get("SUPABASE_URL", None)
        self.db_key = os.environ.get("SUPABASE_KEY", None)
        try:
            self.supabase = create_client(self.db_url, self.db_key)
            if not self.supabase:
                print("Failed to connect to Supabase")
                remote_db = False
        except Exception as e:
            print(f"Error while creating Supabase client: {e}")
            print(
                f"Error while creating Supabase client: {e}",
                "Phantom-Indexer-check_remote",
            )
            remote_db = False

        return remote_db

    def load(self, table, key="url", val="content", START=0, LIMIT=None):

        self.CHUNK_LIMIT = LIMIT if LIMIT else self.CHUNK_LIMIT
        start = START
        end = self.CHUNK_SIZE - 1
        data = {}
        try:
            print("Fetching data from remote DB")
            while True:
                response = (
                    self.supabase.table(table)
                    .select(key, val)
                    .range(start, end)
                    .execute()
                )
                if not response.data:
                    break
                for record in response.data:
                    data[record[key]] = record[val]

                start += self.CHUNK_SIZE
                end += self.CHUNK_SIZE

                print(f"Data fetched from DB: {len(data)}")

                if len(data) >= self.CHUNK_LIMIT:
                    print("CHUNK limit reached")
                    break

            print(f"Data fetched from remote DB: {len(data)}")

        except Exception as e:
            print(f"Error fetching data from index table: {e}")
            if len(data) >= self.CHUNK_SIZE:
                return data
            return None

        return data
