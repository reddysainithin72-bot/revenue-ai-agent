from pathlib import Path
import sqlite3, random
from datetime import date, timedelta
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True); DB=DATA/'revenue.db'
def build_database():
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB); con.executescript((ROOT/'database/schema.sql').read_text())
    products=[(1,'Premium Sneakers','Footwear',120),(2,'Classic Jacket','Apparel',180),(3,'Luxury Watch','Accessories',250),(4,'Leather Bag','Accessories',220),(5,'Premium Hoodie','Apparel',90)]
    con.executemany('INSERT INTO products VALUES (?,?,?,?)',products)
    random.seed(42); sessions=[]; orders=[]; payments=[]; errors=[]; sid=oid=pid=eid=1; start=date(2026,7,29)
    for d in range(60):
        day=start+timedelta(days=d); incident=d>=30
        for _ in range(100):
            device=random.choices(['desktop','mobile','tablet'],[.45,.50,.05])[0]; source=random.choice(['organic','paid','social','direct']); sessions.append((sid,day.isoformat(),device,source))
            base={'desktop':.105,'mobile':.092,'tablet':.085}[device]; prob=base*(.48 if incident and device=='mobile' else .82 if incident else 1)
            if random.random()<prob:
                p=random.choice(products); ok=random.random()<(.90 if not incident else .78); method=random.choice(['card','upi','wallet']); ps='success' if ok else 'failed'; status='completed' if ok else 'cancelled'; orders.append((oid,sid,p[0],day.isoformat(),p[3],status)); payments.append((pid,oid,method,ps)); oid+=1; pid+=1
            if random.random()<(.008 if not incident else .025): errors.append((eid,day.isoformat(),device,random.choice(['checkout_timeout','payment_gateway','api_error','inventory_api']),random.randint(1 if not incident else 2,3 if not incident else 7))); eid+=1
            sid+=1
    con.executemany('INSERT INTO sessions VALUES (?,?,?,?)',sessions); con.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)',orders); con.executemany('INSERT INTO payments VALUES (?,?,?,?)',payments); con.executemany('INSERT INTO application_errors VALUES (?,?,?,?,?)',errors); con.executemany('INSERT INTO deployments VALUES (?,?,?,?)',[(1,'2026-08-28','v2.8.1','checkout-service'),(2,'2026-08-29','v2.8.1','payment-service')]); con.commit(); con.close(); print(DB)
if __name__=='__main__': build_database()
