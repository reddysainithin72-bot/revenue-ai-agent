from database.seed import build_database
from agent.sql_agent import investigate
def test_payment_query():
    build_database(); assert investigate('payment')
