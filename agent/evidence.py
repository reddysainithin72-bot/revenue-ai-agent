def evaluate_evidence(hypothesis,metrics,evidence):
    c=0.; reasons=[]
    if hypothesis=='traffic':
        x=metrics.get('traffic_change_pct',0); c=.90 if x<-20 else .75 if x<-10 else 0
        if c: reasons.append(f'Traffic decreased by {x:.2f}%.')
    elif hypothesis=='conversion':
        x=metrics.get('conversion_change_pct',0); c=.90 if x<-20 else .75 if x<-10 else 0
        if c: reasons.append(f'Overall conversion decreased by {x:.2f}%.')
    elif hypothesis=='device':
        x=metrics.get('mobile_conversion_change_pct',0); c=.92 if x<-30 else .80 if x<-15 else 0
        if c: reasons.append(f'Mobile conversion decreased by {x:.2f}%.')
    elif hypothesis=='payment':
        x=metrics.get('payment_failure_change_pct',0); c=.95 if x>100 else .90 if x>50 else .75 if x>20 else 0
        if c: reasons.append(f'Payment failures increased by {x:.2f}%.')
    elif hypothesis=='technical':
        x=metrics.get('checkout_error_change_pct',0); c=.95 if x>100 else .90 if x>50 else .75 if x>20 else 0
        if c: reasons.append(f'Application errors increased by {x:.2f}%.')
    elif hypothesis=='product': c=.40; reasons.append('Product-level revenue distribution was inspected.')
    if not reasons: c=.20; reasons.append('Current evidence does not strongly support this hypothesis.')
    return {'hypothesis':hypothesis,'confidence':c,'reasons':reasons,'raw_evidence':evidence}
