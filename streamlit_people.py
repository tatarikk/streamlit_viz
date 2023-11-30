import streamlit as st
import psycopg2
from datetime import datetime
import json
import time

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def process_new_records(rows):
    for row in rows:
        list_rows = list(map(str, row))
        json_forms = list_rows[1].replace("'", "")
        loads_json = json.loads(json_forms)

        timestamp = loads_json['timestamp']
        date = datetime.fromtimestamp(float(timestamp))

        image = loads_json['RAM_path']
        person_id = list_rows[0]
        proba = loads_json['proba']
        fps = loads_json['fps']

        st.write(f"{date}")
        st.image(image)
        st.write(f"Person ID: {person_id}")
        st.write(f"FPS:{fps}")
        st.write("-----------------")


# Streamlit UI
i = 0
st.date_input("Выберите дату просмотра людей", key=i)
st.write("-----------------")
message_cache = set()
while True:
    rows = run_query("SELECT * from all_people;")
    process_new_records(rows)

    time.sleep(10)  

    new_rows = run_query("SELECT * from all_people WHERE id > (SELECT MAX(id) FROM all_people);")
    if new_rows:
        process_new_records(new_rows)
