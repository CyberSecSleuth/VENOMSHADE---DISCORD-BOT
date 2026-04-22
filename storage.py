import json
import asyncio
import atexit
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"
SAVE_INTERVAL = 60

_data_cache = {}
_pending_save = False
_save_callback = None
_data_loaded = False


def get_default_data():
    return {
        "confession_count": 0,
        "confessions": {},
        "post_counter": 0
    }


def load_data():
    global _data_cache, _data_loaded
    
    if _data_loaded and _data_cache:
        return _data_cache
    
    file_path = Path(DATA_FILE)
    
    if not file_path.exists():
        _data_cache = get_default_data()
        save_data()
        _data_loaded = True
        return _data_cache
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        _data_cache = {
            "confession_count": loaded.get("confession_count", 0),
            "confessions": loaded.get("confessions", {}),
            "post_counter": loaded.get("post_counter", 0)
        }
    except (json.JSONDecodeError, IOError) as e:
        print(f"[Storage] Error loading data: {e}. Using defaults.")
        _data_cache = get_default_data()
        save_data()
    
    _data_loaded = True
    return _data_cache


def save_data():
    global _pending_save
    
    file_path = Path(DATA_FILE)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(_data_cache, f, indent=2, ensure_ascii=False)
        _pending_save = False
    except IOError as e:
        print(f"[Storage] Error saving data: {e}")


def mark_dirty():
    global _pending_save
    _pending_save = True


def get_state():
    if not _data_loaded:
        load_data()
    return _data_cache


def update_state(key, value):
    global _data_cache
    if not _data_loaded:
        load_data()
    _data_cache[key] = value
    mark_dirty()


async def periodic_save_task(bot):
    while True:
        await asyncio.sleep(SAVE_INTERVAL)
        
        if _pending_save:
            save_data()
            print(f"[Storage] Auto-saved data")


async def setup_periodic_save(bot):
    global _save_callback
    
    bot.loop.create_task(periodic_save_task(bot))
    
    await bot.wait_until_ready()


def setup_shutdown_save():
    atexit.register(lambda: save_data() if _pending_save else None)


def init(bot):
    print("[Storage] Initializing storage...")
    setup_shutdown_save()
    load_data()
    print(f"[Storage] Data loaded: confession_count={_data_cache.get('confession_count', 0)}, confessions={len(_data_cache.get('confessions', {}))}, post_counter={_data_cache.get('post_counter', 0)}")
    bot.loop.create_task(periodic_save_task(bot))
    print("[Storage] Periodic save task started")