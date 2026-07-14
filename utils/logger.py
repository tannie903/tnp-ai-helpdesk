import pandas as pd
from datetime import datetime
import os

def log_query(question, category, response):
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "question": question,
        "category": category,
        "response": response
    }
    file = "data/query_log.csv"
    df = pd.DataFrame([new_row])
    df.to_csv(
        file,
        mode="a",
        header=not os.path.exists(file),
        index=False
    )