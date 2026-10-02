from analysis.metrics import calculate_metrics


def profile_business(state):

    csv_path = state.get("csv_path")

    # Streamlit / real company data
    if csv_path:
        return calculate_metrics(csv_path)

    # Test / development database
    return calculate_metrics()