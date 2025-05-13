import psycopg2


def test_connection():
    conn = psycopg2.connect(
        dbname="feuerwehr_meiringen",
        user="feuerwehr_user",
        password="admin",
        host="localhost",
        port=5432,
    )
    print("✅ Verbindung erfolgreich!")
    conn.close()


def get_connection():
    return psycopg2.connect(
        dbname="feuerwehr_meiringen",
        user="feuerwehr_user",
        password="admin",  # dein Passwort hier einsetzen
        host="localhost",
        port=5432,
    )


if __name__ == "__main__":
    test_connection()
