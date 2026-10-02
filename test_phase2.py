from agent.graph import build_graph
if __name__=='__main__':
    r=build_graph().invoke({'goal':'Our total revenue dropped last month. Find out why.','investigated':[]})
    print('ROOT CAUSE:',r.get('root_cause')); print('CONFIDENCE:',r.get('confidence')); print('INVESTIGATED:',r.get('investigated')); print('EVIDENCE:'); [print('-',x) for x in r.get('evidence_reasons',[])]; print('METRICS:'); [print(k,':',v) for k,v in r.get('metrics',{}).items()]
