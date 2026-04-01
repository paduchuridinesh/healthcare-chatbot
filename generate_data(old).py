import pandas as pd
import json
import random
import os

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

def generate_dynamic_data():
    # 1. Load your actual symptoms list
    try:
        with open('data/symptoms.json', 'r') as f:
            symptoms_data = json.load(f)
            symptoms = list(symptoms_data.keys())
    except FileNotFoundError:
        print("Error: symptoms.json not found in data/ folder.")
        return

    # 2. Define intensity descriptors
    low_intensity = ["slight", "minor", "mild", "a little bit of", "occasional", "small"]
    high_intensity = ["unbearable", "severe", "crushing", "extreme", "constant", "intense", "sharp"]

    training_rows = []

    # 3. Generate phrases for every symptom in your JSON
    for s in symptoms:
        # Generate Low Severity rows (Score 1-3)
        for i in low_intensity:
            training_rows.append({"Phrase": f"I have a {i} {s}", "Severity Score": random.randint(1, 3)})
            training_rows.append({"Phrase": f"My {s} is quite {i}", "Severity Score": random.randint(1, 3)})

        # Generate High Severity rows (Score 7-10)
        for i in high_intensity:
            training_rows.append({"Phrase": f"I have {i} {s}", "Severity Score": random.randint(8, 10)})
            training_rows.append({"Phrase": f"This {s} is {i}", "Severity Score": random.randint(8, 10)})
            training_rows.append({"Phrase": f"I can't stand this {i} {s}", "Severity Score": random.randint(9, 10)})

    # 4. Save to CSV
    df = pd.DataFrame(training_rows)
    df.to_csv('data/severity_data.csv', index=False)
    print(f"✅ Successfully synced with symptoms.json!")
    print(f"✅ Generated {len(df)} rows covering {len(symptoms)} symptoms.")

if __name__ == "__main__":
    generate_dynamic_data()