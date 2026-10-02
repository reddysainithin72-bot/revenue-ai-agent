from database.seed import build_database
from analysis.metrics import calculate_metrics
def test_metrics():
    build_database(); m=calculate_metrics(); assert 'revenue_change_pct' in m; assert 'payment_failure_change_pct' in m
