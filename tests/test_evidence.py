from agent.evidence import evaluate_evidence
def test_payment_evidence():
    assert evaluate_evidence('payment',{'payment_failure_change_pct':166},[])['confidence']>=.9
