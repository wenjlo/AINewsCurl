from config import user,password,host,port,database
import os
from config import TOKEN
os.environ['GEMINI_API_KEY'] = TOKEN
import pymysql
from configparser import ConfigParser
def delete_data():
    connection = pymysql.connect(host=host, port=int(port),
                                 user=user, password=password, database=database)

    cursor = connection.cursor()
    query = """
             WITH RankedData AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER(ORDER BY `time` DESC) AS rn
                FROM
                    news_curl
            )
            DELETE FROM news_curl 
            WHERE news_url IN (SELECT news_url  FROM RankedData WHERE rn > 100)
            ;"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
delete_data()