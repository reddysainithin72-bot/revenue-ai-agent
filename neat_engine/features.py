import numpy as np
FEATURES=['revenue_change_pct','traffic_change_pct','conversion_change_pct','mobile_conversion_change_pct','payment_failure_change_pct','checkout_error_change_pct']
def normalize_metrics(metrics):
    x=np.array([metrics.get(k,0.0) for k in FEATURES],dtype=np.float32); x=np.nan_to_num(x,nan=0,posinf=100,neginf=-100); return np.clip(x/100,-1,1)
