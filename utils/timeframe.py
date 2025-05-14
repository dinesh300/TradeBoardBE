from datetime import datetime

def get_timeframe_label(current_time):
    start_time = datetime(current_time.year, current_time.month, current_time.day, 9, 15)
    if start_time <= current_time <= start_time.replace(hour=15, minute=15):
        index = int((current_time - start_time).total_seconds() / 1800)
        return chr(65 + index) if index < 12 else None
    return None
