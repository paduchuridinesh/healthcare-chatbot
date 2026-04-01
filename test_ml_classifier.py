"""
Direct test of ML classifier to verify mild symptoms are classified as MINOR
"""

from ml_classifier import MLClassifier
from nlp_processor import NLPProcessor

print("="*60)
print("Testing ML Classifier for MINOR classification")
print("="*60)

# Initialize
ml = MLClassifier()
nlp = NLPProcessor()

# Test Case 1: Mild headache, 2 hours
print("\n✅ TEST 1: Mild headache, 2 hours, no red flags")
print("-" * 60)
severity_label, severity_score = nlp.classify_severity_nlp("mild")
print(f"  Severity: {severity_label} (score: {severity_score})")
duration_hours = 2
has_red_flags = 0
symptom_key = "headache"

prediction, probabilities, confidence = ml.predict(
    severity_score=severity_score,
    duration_hours=duration_hours,
    has_red_flags=has_red_flags,
    symptom_key=symptom_key
)

classification = ml.get_classification_name(prediction)
print(f"  Duration: {duration_hours} hours")
print(f"  Red flags: {has_red_flags}")
print(f"  Symptom criticality: 4")
print(f"\n  📊 ML Prediction: {classification}")
print(f"  Probabilities: Minor={probabilities[0]:.2%}, Consultation={probabilities[1]:.2%}, Emergency={probabilities[2]:.2%}")
print(f"  Confidence: {confidence:.2%}")
print(f"\n  Expected: MINOR")
print(f"  Result: {'✅ PASS' if classification == 'MINOR' else '❌ FAIL'}")

# Test Case 2: Mild stomach pain, 3 hours
print("\n✅ TEST 2: Mild stomach pain, 3 hours, no red flags")
print("-" * 60)
severity_label, severity_score = nlp.classify_severity_nlp("not too bad")
print(f"  Severity: {severity_label} (score: {severity_score})")
duration_hours = 3
has_red_flags = 0
symptom_key = "stomach_pain"

prediction, probabilities, confidence = ml.predict(
    severity_score=severity_score,
    duration_hours=duration_hours,
    has_red_flags=has_red_flags,
    symptom_key=symptom_key
)

classification = ml.get_classification_name(prediction)
print(f"  Duration: {duration_hours} hours")
print(f"  Red flags: {has_red_flags}")
print(f"\n  📊 ML Prediction: {classification}")
print(f"  Probabilities: Minor={probabilities[0]:.2%}, Consultation={probabilities[1]:.2%}, Emergency={probabilities[2]:.2%}")
print(f"  Confidence: {confidence:.2%}")
print(f"\n  Expected: MINOR")
print(f"  Result: {'✅ PASS' if classification == 'MINOR' else '❌ FAIL'}")

# Test Case 3: Moderate headache, 3 days
print("\n✅ TEST 3: Moderate headache, 3 days, no red flags")
print("-" * 60)
severity_label, severity_score = nlp.classify_severity_nlp("moderate pain")
print(f"  Severity: {severity_label} (score: {severity_score})")
duration_hours = 72
has_red_flags = 0
symptom_key = "headache"

prediction, probabilities, confidence = ml.predict(
    severity_score=severity_score,
    duration_hours=duration_hours,
    has_red_flags=has_red_flags,
    symptom_key=symptom_key
)

classification = ml.get_classification_name(prediction)
print(f"  Duration: {duration_hours} hours (3 days)")
print(f"  Red flags: {has_red_flags}")
print(f"\n  📊 ML Prediction: {classification}")
print(f"  Probabilities: Minor={probabilities[0]:.2%}, Consultation={probabilities[1]:.2%}, Emergency={probabilities[2]:.2%}")
print(f"  Confidence: {confidence:.2%}")
print(f"\n  Expected: CONSULTATION")
print(f"  Result: {'✅ PASS' if classification == 'CONSULTATION' else '❌ FAIL'}")

# Test Case 4: Severe chest pain
print("\n✅ TEST 4: Severe chest pain, 1 hour")
print("-" * 60)
severity_label, severity_score = nlp.classify_severity_nlp("unbearable")
print(f"  Severity: {severity_label} (score: {severity_score})")
duration_hours = 1
has_red_flags = 1
symptom_key = "chest_pain"

prediction, probabilities, confidence = ml.predict(
    severity_score=severity_score,
    duration_hours=duration_hours,
    has_red_flags=has_red_flags,
    symptom_key=symptom_key
)

classification = ml.get_classification_name(prediction)
print(f"  Duration: {duration_hours} hour")
print(f"  Red flags: {has_red_flags}")
print(f"\n  📊 ML Prediction: {classification}")
print(f"  Probabilities: Minor={probabilities[0]:.2%}, Consultation={probabilities[1]:.2%}, Emergency={probabilities[2]:.2%}")
print(f"  Confidence: {confidence:.2%}")
print(f"\n  Expected: EMERGENCY")
print(f"  Result: {'✅ PASS' if classification == 'EMERGENCY' else '❌ FAIL'}")

print("\n" + "="*60)
print("Testing complete!")
print("="*60)
