import mysql.connector

def get_all_skills():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="153289",
        database="portfolio"
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT skill_id, skill_desc, level FROM skill")
    skills = cursor.fetchall()
    conn.close()
    return skills