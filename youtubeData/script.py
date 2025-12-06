import psycopg2
from psycopg2 import extras
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta


API_KEY = 'AIzaSyDyW3KY_HzAfljw2z-BhQ9jAX1IeV9v1nY'

# Konfiguracja Bazy Danych
DB_HOST = "212.132.76.195"
DB_PORT = "5433"
DB_NAME = "hacknation_db"
DB_USER = "hack"
DB_PASS = "HackNation!"


def pobierz_filmy_z_okresu(api_key, conn, szukany_hasztag, data_koncowa_str=None):

    cur = conn.cursor()


    try:
        cur.execute("SELECT id FROM tag WHERE tag_name = %s", (szukany_hasztag,))
        result = cur.fetchone()

        if result:
            tag_db_id = result[0]
        else:
            print(f"POMINIĘTO: Tag '{szukany_hasztag}' nie istnieje w tabeli 'tag'.")
            return

    except Exception as e:
        print(f"Błąd podczas pobierania ID tagu: {e}")
        return


    try:
        if data_koncowa_str:
            data_koncowa = datetime.strptime(data_koncowa_str, "%Y-%m-%d")
            data_koncowa = data_koncowa.replace(hour=23, minute=59, second=59)
        else:
            data_koncowa = datetime.now()

        data_poczatkowa = data_koncowa - timedelta(days=7)

        published_before = data_koncowa.isoformat() + 'Z'
        published_after = data_poczatkowa.isoformat() + 'Z'

    except ValueError:
        print("Błąd: Nieprawidłowy format daty.")
        return

    youtube = build('youtube', 'v3', developerKey=api_key)

    comments_data_to_insert = []

    try:
        print(f"[{szukany_hasztag}] Szukam filmu (ID tagu: {tag_db_id})...")


        search_request = youtube.search().list(
            part="id,snippet",
            q=szukany_hasztag,
            type="video",
            publishedAfter=published_after,
            publishedBefore=published_before,
            videoDuration="medium",
            order="viewCount",
            maxResults=1,
            relevanceLanguage='pl',
            regionCode='PL'
        )
        search_response = search_request.execute()

        if not search_response.get('items'):
            print(f"   -> Nie znaleziono filmów w tym okresie.")
            return

        video_item = search_response['items'][0]
        video_id = video_item['id']['videoId']
        video_title = video_item['snippet']['title']

        print(f"   -> Znaleziono: {video_title[:50]}...")

        # Krok B: Pobieranie komentarzy
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        comments_response = comments_request.execute()

        items = comments_response.get('items', [])


        cur.execute("SELECT COALESCE(MAX(id), 0) FROM komentarz_youtube")
        max_id_row = cur.fetchone()
        current_max_id = max_id_row[0] if max_id_row else 0


        for i, item in enumerate(items):

            new_id = current_max_id + 1 + i

            text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            clean_text = text.strip()


            comments_data_to_insert.append((new_id, clean_text, tag_db_id))


        if comments_data_to_insert:

            query = "INSERT INTO komentarz_youtube (id, komentarz, tag_id) VALUES %s"

            extras.execute_values(cur, query, comments_data_to_insert)

            conn.commit()
            print(f"   -> SUKCES: Wgrano {len(comments_data_to_insert)} komentarzy (ID od {current_max_id + 1}).")
        else:
            print("   -> Pobrano 0 komentarzy.")

    except HttpError as e:
        if e.resp.status == 403:
            print("   -> Komentarze są wyłączone pod tym filmem.")
        else:
            print(f"   -> Błąd API YouTube: {e}")
    except Exception as e:
        conn.rollback()
        print(f"   -> Wystąpił błąd: {e}")
    finally:
        cur.close()



if __name__ == "__main__":

    tagsTab = [
        "giełda",
        "w co inwestować",
        "elektrownia wodna",
        "fotowoltaika",
        "awaria prądu",
        "cpk",
        "linia kolejowa",
        "budowa autostrad",
        "cyberbezpieczeństwo",
        "technologia smartfony ",
        "praca w IT",
        "nieruchomości"
    ]

    print("Łączenie z bazą danych...")
    try:

        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )

        print("Rozpoczynam pobieranie danych...")
        data_input = ""

        for tag in tagsTab:
            pobierz_filmy_z_okresu(API_KEY, connection, tag, data_input.strip())

    except psycopg2.Error as e:
        print(f"Błąd połączenia z bazą danych: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            print("\nPołączenie z bazą zostało zamknięte.")