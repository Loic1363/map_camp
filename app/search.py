import requests

def rechercher_lieu_api(lieu):
    if not lieu:
        return None
    url = f"https://nominatim.openstreetmap.org/search?q={lieu}&format=json&limit=1"
    headers = {"User-Agent": "MapApp-TkinterSearch"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        else:
            return None
    except:
        return None
