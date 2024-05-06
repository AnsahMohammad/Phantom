import os
from supabase import create_client, Client
import json

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
        
        print("Remote database : ", self.remote_db)
        print("DB Ready")

    def add(self, key, value, title=None):
        if self.remote_db:
            try:
                data, count = self.supabase.table(self.table_name).insert({"url": key, "content": json.dumps(value), "title": title}).execute()
            except Exception as e:
                print(f"\nError inserting record into {self.table_name} table: {e}\n")
                return False
            return True

        # print("value is of length : ", len(value))            
        self.data[key] = value

    def fetch_visited(self):
        visited = set()
        if self.resume and self.remote_db:
            # if resume the execution and remote db available
            response = self.supabase.table('index').select('url').execute()
            for row in response['data']:
                visited.add(row['url'])
            print("Visited URLs fetched from remote DB : ",len(visited))

        return visited

    def save(self):
        if self.remote_db:
            return
        table_name = self.table_name + ".json"
        with open(table_name, "w") as f:
            json.dump(self.data, f)

