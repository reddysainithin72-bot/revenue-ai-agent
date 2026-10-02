import plotly.graph_objects as go
def bar(title,labels,values):
    f=go.Figure(go.Bar(x=labels,y=values,text=[f'{v:.2f}' for v in values],textposition='auto')); f.update_layout(title=title,height=320); return f
def hypothesis_chart(scores): return bar('NEAT Investigation Strategy',list(scores),list(scores.values()))
