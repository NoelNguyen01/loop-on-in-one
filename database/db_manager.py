import json
import os

class DatabaseManager:
    def __init__(self):
        self.data = {}
        self.load()
    
    def load(self):
        try:
            with open("database/data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"users": {}, "guilds": {}}
            self.save()
    
    def save(self):
        os.makedirs("database", exist_ok=True)
        with open("database/data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {"balance": 0, "warns": 0}
            self.save()
        return self.data["users"][uid]
    
    def get_guild(self, guild_id):
        gid = str(guild_id)
        if gid not in self.data["guilds"]:
            self.data["guilds"][gid] = {"autorole": None, "prefix": "!"}
            self.save()
        return self.data["guilds"][gid]
