from pathlib import Path
import sqlite3,pandas as pd
TABLES=['sessions','orders','payments','products','application_errors','deployments']
def build_database_from_csv(uploaded,output_path):
    output_path=Path(output_path); output_path.parent.mkdir(parents=True,exist_ok=True)
    if output_path.exists(): output_path.unlink()
    con=sqlite3.connect(output_path)
    try:
        for name in TABLES:
            if name in uploaded: pd.read_csv(uploaded[name]).to_sql(name,con,if_exists='replace',index=False)
    finally: con.close()
    return output_path
