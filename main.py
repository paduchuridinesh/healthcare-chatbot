from chatbot_engine import TriageBot

def run_chat():
    bot = TriageBot()
    print("--- MediGuide Hospital Assistant ---")

    user_input = input("Bot: Hello! How can I help you today?\nYou: ").strip()
    symptoms_found = bot.extract_symptoms(user_input)

    if not symptoms_found:
        print("Bot: I'm sorry, I didn't recognize that symptom. Please try 'headache' or 'fever'.")
        return

    symptom = symptoms_found[0]  # Use highest-scored symptom
    symptom_display = symptom.replace('_', ' ').title()
    print(f"Bot: I understand you're experiencing {symptom_display}.")

    duration_input = input("Bot: How long have you had this symptom? (e.g. '2 days', '3 hours')\nYou: ").strip()
    duration_info = bot.extract_duration(duration_input)
    if duration_info == (None, None):
        print("Bot: Couldn't parse duration, defaulting to 1 day.")
        duration_info = (1, 'days')

    severity_input = input("Bot: How severe is it? (e.g. 'mild', 'moderate', 'very painful', or 1-10)\nYou: ").strip()
    severity_data = bot.extract_severity(severity_input)
    if not severity_data:
        print("Bot: Couldn't parse severity, defaulting to moderate (5).")
        severity_data = ('moderate', 5)

    questions = bot.symptoms_data[symptom]["questions"]
    user_answers = []
    for q in questions:
        ans = input(f"Bot: {q}\nYou: ").strip()
        user_answers.append(ans)

    result = bot.classify_issue_ml(
        symptom=symptom,
        duration_info=duration_info,
        severity_data=severity_data,
        follow_up_answers=user_answers
    )
    print("\n--- Final Recommendation ---")
    print(result["message"])

if __name__ == "__main__":
    run_chat()