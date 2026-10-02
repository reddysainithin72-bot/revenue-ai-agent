from database.seed import build_database
from agent.graph import build_graph
def test_graph():
    build_database(); r=build_graph().invoke({'goal':'Why did revenue fall?','investigated':[]}); assert r.get('status')=='investigation_complete'; assert r.get('root_cause')
