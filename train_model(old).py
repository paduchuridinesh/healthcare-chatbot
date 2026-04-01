import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import pickle
import os

# 1. Create directory for the saved model
if not os.path.exists('models'):
    os.makedirs('models')

# 2. Load the dynamic data you just generated
data = pd.read_csv('data/severity_data.csv')

# 3. Vectorization: Convert text to numbers
# TF-IDF helps the model understand which words (like "crushing") are important
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['Phrase'])
y = data['Severity Score']

# 4. Training: Teach the model the patterns
model = LinearRegression()
model.fit(X, y)

# 5. Persistence: Save the 'brain' to a file
# We save both the vectorizer and the model together
with open('models/severity_model.pkl', 'wb') as f:
    pickle.dump((vectorizer, model), f)

print("✅ Model trained successfully!")
print("✅ Saved 'models/severity_model.pkl'")