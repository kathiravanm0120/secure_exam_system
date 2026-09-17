"""Local append-only blockchain used for development and testing."""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

LEDGER_PATH = Path(os.getenv("BLOCKCHAIN_LEDGER_PATH", "./data/blockchain.json"))
_LEDGER_LOCK = Lock()

def _utc_iso(): return datetime.now(timezone.utc).isoformat()
def _canonical(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def _block_hash(block): return hashlib.sha256(_canonical({k:v for k,v in block.items() if k != 'hash'})).hexdigest()

def _ensure():
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LEDGER_PATH.exists(): return
    genesis={"index":0,"timestamp":_utc_iso(),"event":"GENESIS","data":{"system":"Secure Exam System","version":"local"},"previous_hash":"0"*64}
    genesis["hash"]=_block_hash(genesis)
    LEDGER_PATH.write_text(json.dumps([genesis], indent=2), encoding="utf-8")

def _load():
    _ensure(); return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
def _save(chain):
    tmp=LEDGER_PATH.with_suffix('.tmp'); tmp.write_text(json.dumps(chain, indent=2), encoding='utf-8'); tmp.replace(LEDGER_PATH)

class LocalLedger:
    def add_event(self,event,data):
        with _LEDGER_LOCK:
            chain=_load(); block={"index":len(chain),"timestamp":_utc_iso(),"event":event,"data":data,"previous_hash":chain[-1]["hash"]}; block["hash"]=_block_hash(block); chain.append(block); _save(chain); return block
    def get_chain(self):
        with _LEDGER_LOCK: return _load()
    def verify_chain(self):
        with _LEDGER_LOCK:
            c=_load()
            for i,b in enumerate(c):
                if b.get('hash') != _block_hash(b): return {"valid":False,"bad_index":i,"reason":"Block hash mismatch"}
                expected='0'*64 if i==0 else c[i-1].get('hash')
                if b.get('previous_hash') != expected: return {"valid":False,"bad_index":i,"reason":"Broken previous-hash link"}
            return {"valid":True,"blocks":len(c),"last_hash":c[-1]['hash']}
    def find_question_events(self,question_id):
        return [b for b in self.get_chain() if b.get('data',{}).get('question_id')==question_id]

# Backwards-compatible functions
_default = LocalLedger()
add_event = _default.add_event
get_chain = _default.get_chain
verify_chain = _default.verify_chain
find_question_events = _default.find_question_events
