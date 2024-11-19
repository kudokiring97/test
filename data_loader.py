import pandas as pd
import snowflake.connector

def load_air_quality_data(serial_no=None):
    conn = snowflake.connector.connect(
        user='ppq1918',
        password='kdms1565**ZX',
        account='pzzyzcz-sn42771',
        warehouse='COMPUTE_WH',
        database='air365',
        schema='test'
    )

    query = "SELECT * FROM measurements "

    if serial_no:
        query += f" WHERE serial_no = '{serial_no}' ORDER BY date"  # serial_no 필터 추가

    # SQL 쿼리를 사용해 데이터 로드
    df = pd.read_sql_query(query, conn)
    
    conn.close()

    return df
