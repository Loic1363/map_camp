import json
import os

def charger_lieux(fichier="lieux.json"):
    if os.path.exists(fichier):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    else:
        return {}

def sauvegarder_lieux(lieux, fichier="lieux.json"):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(lieux, f, ensure_ascii=False, indent=2)

def exporter_lieux(lieux, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lieux, f, ensure_ascii=False, indent=2)

def importer_lieux(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
