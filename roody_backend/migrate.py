import psycopg2
import dateutil.parser
import datetime
import os

conn = psycopg2.connect(host="postgres", dbname="postgres", user="postgres", password=os.environ["POSTGRES_PASS"])
cur = conn.cursor()

print(cur.execute("CREATE TABLE IF NOT EXISTS roody(temperature real, humidity real, carbonous real, smoke real, time_stamp timestamp);"));
print(cur.execute("CREATE TABLE IF NOT EXISTS limits(temperature real, humidity real, carbonous real, smoke real);"));
print(cur.execute("INSERT INTO limits(temperature, humidity, carbonous, smoke) VALUES (40.0, 60.0, 60.0, 60.0);"));
print(conn.commit());

