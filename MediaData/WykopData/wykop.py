import requests
import time
import psycopg2
from unidecode import unidecode

# --- 1. KONFIGURACJA BAZY DANYCH ---
DB_HOST = "212.132.76.195"
DB_PORT = "5433"
DB_NAME = "hacknation_db"
DB_USER = "hack"
DB_PASS = "HackNation!"

# --- 2. KONFIGURACJA WYKOP API ---
API_KEY = 'w5ec5c2895e37c74fc261aaf72910f3422'
SECRET_KEY = 'c8560f9f2c7b51ac5ce29f620b0f89cf'

TARGET_POSTS_PER_TAG = 300


class WykopScraperToDB:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.token = None
        self.base_url = "https://wykop.pl/api/v3"
        self.conn = None
        self.cursor = None

    def connect_db(self):
        """Łączenie z bazą PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            self.cursor = self.conn.cursor()
            print("✅ Połączono z bazą danych PostgreSQL.")
        except Exception as e:
            print(f"❌ Błąd połączenia z bazą: {e}")
            exit()

    def authenticate(self):
        """Logowanie do API Wykop v3"""
        try:
            res = requests.post(f"{self.base_url}/auth", json={"data": {"key": self.key, "secret": self.secret}})
            if res.status_code == 200:
                self.token = res.json().get('data', {}).get('token')
                print("✅ Zalogowano do API Wykop.")
            else:
                print(f"❌ Błąd logowania API: {res.text}")
                exit()
        except Exception as e:
            print(f"Błąd krytyczny auth: {e}")
            exit()

    def get_tags_from_db(self):
        """Pobiera listę tagów z bazy danych"""
        if not self.cursor: return []
        query = "SELECT id, tag_name FROM tag"
        self.cursor.execute(query)
        tags = self.cursor.fetchall()
        print(f"ℹ️ Pobrano {len(tags)} tagów do monitorowania z bazy danych.")
        return tags

    def get_tag_stream(self, tag_name, page=1):
        if not self.token: return []
        clean_tag = unidecode(tag_name).lower().replace(" ", "")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        url = f"{self.base_url}/tags/{clean_tag}/stream?page={page}&sort=all"

        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                return res.json().get('data', [])
            return []
        except:
            return []

    def save_post(self, wykop_id, tag_id, content):
        """
        Zapisuje post do tabeli post_wykop.
        POPRAWKA: Jawnie podajemy ID wpisu z Wykopu do kolumny 'id'.
        """
        # Używamy INSERT ... ON CONFLICT DO NOTHING, aby uniknąć błędu jeśli wpis już istnieje
        # Jeśli Twoja baza nie ma klucza głównego na ID, zadziała zwykły INSERT,
        # ale dodajemy obsługę błędów DuplicateKey.

        sql = "INSERT INTO post_wykop (id, tag_id, post) VALUES (%s, %s, %s)"

        try:
            self.cursor.execute(sql, (wykop_id, tag_id, content))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()  # Cofamy transakcję w przypadku duplikatu
            # To nie jest błąd krytyczny, po prostu wpis już jest
            return False
        except Exception as e:
            print(f"❌ Błąd zapisu do DB (ID: {wykop_id}): {e}")
            self.conn.rollback()
            return False

    def run(self):
        self.connect_db()
        self.authenticate()

        tags = self.get_tags_from_db()

        for db_tag_id, db_tag_name in tags:
            print(f"\n--> Przetwarzanie tagu: {db_tag_name} (ID: {db_tag_id})")

            posts_collected = 0
            page = 1
            max_empty_pages = 3
            empty_pages_cnt = 0

            while posts_collected < TARGET_POSTS_PER_TAG:
                entries = self.get_tag_stream(db_tag_name, page)

                if not entries:
                    empty_pages_cnt += 1
                    if empty_pages_cnt >= max_empty_pages:
                        print(f"   Koniec danych dla tagu {db_tag_name}.")
                        break
                    page += 1
                    continue

                empty_pages_cnt = 0

                for entry in entries:
                    # POPRAWKA: Pobieramy ID wpisu z Wykopu
                    wykop_id = entry.get('id')

                    content = entry.get('content', '')
                    if not content and 'source' in entry:
                        content = entry.get('source', {}).get('label', '')

                    # Sprawdzamy czy mamy ID i Treść
                    if wykop_id and content:
                        success = self.save_post(wykop_id, db_tag_id, content)
                        if success:
                            posts_collected += 1

                    if posts_collected >= TARGET_POSTS_PER_TAG:
                        break

                print(f"   Pobrano {posts_collected}/{TARGET_POSTS_PER_TAG} (Strona {page})")
                page += 1
                time.sleep(1)

        print("\n🏁 Zakończono pobieranie.")
        if self.conn:
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    scraper = WykopScraperToDB(API_KEY, SECRET_KEY)
    scraper.run()