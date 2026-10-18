import os
import json
import urllib.request
import urllib.parse
import time

OUTPUT_DIR = r"C:\Users\gorre\.gemini\antigravity\scratch\malaysia-trip-2027\assets\images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "MalaysiaFamilyVoyageBot/1.0 (https://example.org; contact@example.org) Python-urllib/3.x"
}

TARGETS = [
    # 20 Spots
    ("stadthuys", ["The Stadthuys Malacca", "Stadthuys Melaka"]),
    ("melaka-cruise", ["Malacca River", "Melaka River Cruise", "Malacca River night"]),
    ("baba-nyonya", ["Baba Nyonya Heritage Museum", "Peranakan Museum Malacca", "Heeren Street Malacca"]),
    ("nancys-kitchen", ["Nyonya cuisine", "Peranakan food", "Kuih pie tee", "Ayam pongteh"]),
    ("jonker88", ["Jonker Walk Melaka", "Jonker Street Malacca", "Cendol Malaysia"]),
    ("putra-mosque", ["Putra Mosque Putrajaya", "Masjid Putra"]),
    ("putrajaya-cruise", ["Seri Wawasan Bridge Putrajaya", "Putrajaya Lake", "Cruise Tasik Putrajaya"]),
    ("klcc-park", ["Petronas Twin Towers night", "KLCC Park", "Petronas Panorama"]),
    ("hakka-kl", ["Hakka cuisine", "Chinese cuisine Malaysia", "Kuala Lumpur restaurant"]),
    ("aquaria-klcc", ["Aquaria KLCC", "Aquarium tunnel shark", "Underwater tunnel aquarium"]),
    ("madam-kwans", ["Nasi lemak Malaysia", "Satay Malaysia", "Malaysian cuisine"]),
    ("petrosains", ["Suria KLCC interior", "Petrosains", "Science museum interactive"]),
    ("jalan-alor", ["Jalan Alor", "Jalan Alor night", "Bukit Bintang street food"]),
    ("batu-caves", ["Batu Caves stairs", "Batu Caves Murugan"]),
    ("kwai-chai-hong", ["Petaling Street Kuala Lumpur", "Chinatown Kuala Lumpur", "Dim sum egg tart"]),
    ("central-market", ["Central Market Kuala Lumpur", "Sultan Abdul Samad Building"]),
    ("islamic-museum", ["Islamic Arts Museum Malaysia", "Islamic Arts Museum dome"]),
    ("trx-mall", ["The Exchange 106", "Tun Razak Exchange", "TRX Kuala Lumpur"]),
    ("pavilion-eslite", ["Pavilion Kuala Lumpur", "Bukit Bintang Kuala Lumpur"]),
    ("mitsui-mop", ["KLIA2 interior", "Sepang Malaysia", "Outlet mall interior"]),
    # Extra banners & hotels
    ("hero-malaysia", ["Petronas Twin Towers Kuala Lumpur", "Putrajaya mosque sunset"]),
    ("day1-flight", ["AirAsia Airbus A320", "Kuala Lumpur International Airport"]),
    ("day8-return", ["Kuala Lumpur International Airport Terminal 2", "Airplane wing sunrise"]),
    ("hotel-ibis", ["Melaka hotel", "Malacca cityscape"]),
    ("hotel-pullman", ["Kuala Lumpur luxury hotel suite", "KLCC skyline"]),
    ("hotel-movenpick", ["Sepang hotel resort", "Movenpick hotel"])
]

def search_wikimedia_image(queries):
    for q in queries:
        params = urllib.parse.urlencode({
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {q}",
            "gsrnamespace": 6,
            "gsrlimit": 5,
            "prop": "imageinfo",
            "iiprop": "url|dimensions|mime",
            "iiurlwidth": 1200,
            "format": "json"
        })
        url = f"https://commons.wikimedia.org/w/api.php?{params}"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = data.get("query", {}).get("pages", {})
                # Sort pages by index
                for pid, pdata in sorted(pages.items(), key=lambda x: x[1].get("index", 99)):
                    iinfo = pdata.get("imageinfo", [{}])[0]
                    mime = iinfo.get("mime", "")
                    if mime not in ("image/jpeg", "image/png", "image/webp"):
                        continue
                    img_url = iinfo.get("thumburl") or iinfo.get("url")
                    width = iinfo.get("thumbwidth") or iinfo.get("width", 0)
                    if img_url and width >= 500:
                        return img_url, pdata.get("title", "")
        except Exception as e:
            print(f"Search error for {q}: {e}")
    return None, None

def main():
    manifest = {}
    for item_id, queries in TARGETS:
        out_path = os.path.join(OUTPUT_DIR, f"{item_id}.jpg")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"[SKIP] {item_id}.jpg already exists ({os.path.getsize(out_path)} bytes)")
            manifest[item_id] = f"./assets/images/{item_id}.jpg"
            continue
        
        img_url, title = search_wikimedia_image(queries)
        if img_url:
            try:
                req = urllib.request.Request(img_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    content = resp.read()
                    if len(content) > 5000:
                        with open(out_path, "wb") as f:
                            f.write(content)
                        print(f"[OK] {item_id}.jpg <- {title} ({len(content)//1024} KB)")
                        manifest[item_id] = f"./assets/images/{item_id}.jpg"
                    else:
                        print(f"[WARN] Too small for {item_id}")
            except Exception as e:
                print(f"[ERR] Download failed for {item_id}: {e}")
        else:
            print(f"[MISS] No image found for {item_id}")
        time.sleep(0.3)

    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Done! Downloaded {len(manifest)}/{len(TARGETS)} images.")

if __name__ == "__main__":
    main()
