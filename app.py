"""
MediGuide - Hospital Guidance Chatbot
Flask API with NLP and ML Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_engine import TriageBot

app = Flask(__name__)
CORS(app)

# Initialize MediGuide bot
bot = TriageBot()
sessions = {}

# Chatbot name and disclaimer
CHATBOT_NAME = "MediGuide"
DISCLAIMER = (
    "ℹ️ **Disclaimer:** This guidance is for informational purposes only and does not replace "
    "professional medical consultation. Always consult with a qualified healthcare provider for medical advice."
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get("user_id", "default_user")
    message = data.get("message", "").strip()

    # Initialize session if new user
    if user_id not in sessions:
        sessions[user_id] = {
            "step": "START",
            "symptom": None,
            "duration": None,
            "severity": None,
            "severity_score": None,
            "answers": [],
            "disclaimer_shown": False
        }

    state = sessions[user_id]

    # === EMERGENCY CHECK (HIGHEST PRIORITY - CHECK AT EVERY INPUT) ===
    is_emergency, emergency_msg = bot.detect_emergency(message)
    if is_emergency:
        sessions[user_id] = {
            "step": "COMPLETED",
            "symptom": None,
            "duration": None,
            "severity": None,
            "severity_score": None,
            "answers": [],
            "disclaimer_shown": True
        }
        return jsonify({
            "reply": emergency_msg,
            "decision": "EMERGENCY",
            "options": ["Start Over"]
        })

    # === GREETING DETECTION ===
    if bot.detect_greeting(message):
        if state["step"] == "START":
            return jsonify({
                "reply": f"Hello! I'm **{CHATBOT_NAME}**, your Hospital Guidance Assistant. 🏥\n\n"
                        "I'm here to help guide you based on your symptoms. "
                        "Please describe the main problem or symptom you are experiencing.",
                "options": []
            })

    # Handle Restart/Reset
    if state["step"] == "COMPLETED":
        if any(word in message.lower() for word in ["start", "new", "hi", "hello", "restart"]):
            sessions[user_id] = {
                "step": "START",
                "symptom": None,
                "duration": None,
                "severity": None,
                "severity_score": None,
                "answers": [],
                "disclaimer_shown": False
            }
            return jsonify({
                "reply": f"Hello! I'm **{CHATBOT_NAME}**, your Hospital Guidance Assistant. 🏥\n\n"
                        "How can I help you today? Please describe your symptoms.",
                "options": []
            })
        return jsonify({
            "reply": "I'm here if you need anything else. You can say 'Start Over' to begin a new assessment.",
            "options": ["Start Over"]
        })

    # === STEP 1: SYMPTOM COLLECTION ===
    if state["step"] == "START":
        symptoms_found = bot.extract_symptoms(message)
        
        if symptoms_found:
            symptom = symptoms_found[0]  # Take the highest scored symptom
            state["symptom"] = symptom
            state["step"] = "DURATION"
            
            # Convert symptom key to readable name
            symptom_display = symptom.replace('_', ' ').title()
            
            reply = (f"I understand you're experiencing **{symptom_display}**. "
                    f"To help me assess this better, how long have you been experiencing this symptom?\n\n"
                    f"*(For example: '2 days', '3 hours', 'just started today')*")
            return jsonify({"reply": reply, "options": []})
        
        return jsonify({
            "reply": "I'm sorry, I didn't quite catch that. Could you describe your symptom more specifically?\n\n"
                    "*(For example: 'I have a headache', 'My stomach hurts', or 'I have a cough')*",
            "options": []
        })

    # === STEP 2: DURATION ===
    if state["step"] == "DURATION":
        duration_info = bot.extract_duration(message)
        
        # Validate: re-ask if no time reference detected
        if duration_info == (None, None):
            return jsonify({
                "reply": "I couldn't understand how long you've had this symptom. Could you describe it like:\n\n"
                        "*(e.g. **'2 days'**, **'3 hours'**, **'since yesterday'**, **'just started today'**)*",
                "options": []
            })
        
        state["duration"] = duration_info
        state["step"] = "SEVERITY"
        
        reply = ("Thank you. Now, how severe is your symptom?\n\n"
                "You can describe it in your own words — "
                "for example: *'mild'*, *'hurts a lot'*, *'unbearable'*, *'not too bad'*.")
        return jsonify({"reply": reply, "options": []})

    # === STEP 3: SEVERITY ===
    if state["step"] == "SEVERITY":
        severity_data = bot.extract_severity(message)
        
        if severity_data:
            severity_label, severity_score = severity_data
            state["severity"] = severity_label
            state["severity_score"] = severity_score
            state["step"] = "FOLLOW_UP_Q1"
            
            # Start with first follow-up question
            symptom = state["symptom"]
            questions = bot.symptoms_data[symptom]["questions"]
            
            reply = f"Understood, thank you. Now, I have a few more questions to better assess your situation.\n\n{questions[0]}"
            return jsonify({"reply": reply, "options": []})
        else:
            return jsonify({
                "reply": "I didn't quite catch the severity. Please describe it in your own words\n\n"
                        "*(e.g. 'mild', 'a little pain', 'moderate', 'very painful', 'unbearable', or a number 1-10)*",
                "options": []
            })

    # === STEP 4-N: FOLLOW-UP QUESTIONS ===
    symptom = state["symptom"]
    questions = bot.symptoms_data[symptom]["questions"]
    
    # We're in follow-up question mode
    if state["step"].startswith("FOLLOW_UP_Q"):
        # Determine the current question being answered
        current_q_index = len(state["answers"])
        current_question = questions[current_q_index]
        
        # Check if this is a Yes/No question.
        # Only flag as yes/no when the question genuinely expects a binary answer.
        # Avoid bare 'is' which triggers on open questions like "Where is the pain?"
        YES_NO_TRIGGERS = ["are you", "do you", "can you", "have you", "did you", "is there", "is it"]
        is_yes_no_q = "?" in current_question and any(
            trigger in current_question.lower() for trigger in YES_NO_TRIGGERS
        )
        
        # Validate Yes/No questions — re-ask if answer is unclear
        if is_yes_no_q:
            yes_no = bot.nlp.extract_yes_no(message.lower())
            if yes_no is None:
                return jsonify({
                    "reply": f"I need a **Yes** or **No** for this question:\n\n{current_question}",
                    "options": ["Yes", "No"]
                })
        
        # Save the validated answer
        state["answers"].append(message)
        
        # Calculate next question index
        current_q_num = len(state["answers"])
        
        # Check if more questions remain
        if current_q_num < len(questions):
            state["step"] = f"FOLLOW_UP_Q{current_q_num + 1}"
            next_question = questions[current_q_num]
            
            # For yes/no questions, provide options (using same safe triggers)
            if "?" in next_question and any(
                trigger in next_question.lower() for trigger in YES_NO_TRIGGERS
            ):
                return jsonify({
                    "reply": next_question,
                    "options": ["Yes", "No"]
                })
            
            return jsonify({"reply": next_question, "options": []})
        
        # === FINAL CLASSIFICATION USING ML ===
        else:
            # Use ML classifier for final decision
            result = bot.classify_issue_ml(
                symptom=symptom,
                duration_info=state["duration"],
                severity_data=(state["severity"], state["severity_score"]),
                follow_up_answers=state["answers"]
            )
            
            state["step"] = "COMPLETED"
            
            # Build response based on decision
            final_msg = result["message"]
            
            # Add specific guidance based on decision type
            if result["decision"] == "MINOR":
                final_msg += f"\n\n**📋 Home Care Recommendations:**\n{result['home_care']}"
                final_msg += f"\n\n**⚠️ Warning Signs - Seek Care If:**\n{result['warning_signs']}"
            
            # Add disclaimer if not shown yet
            if not state["disclaimer_shown"]:
                final_msg += f"\n\n{DISCLAIMER}"
                state["disclaimer_shown"] = True
            
            final_msg += "\n\n**I hope you feel better soon!** 🌟"
            
            response = {
                "reply": final_msg,
                "decision": result["decision"],
                "dept": result.get("dept"),
                "options": ["Start Over"]
            }
            
            # Include doctor list if consultation required
            if result["decision"] == "CONSULTATION":
                doctors = bot.get_doctors_for_dept(result["dept"])
                response["doctors"] = doctors
            
            return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "chatbot": CHATBOT_NAME, "version": "2.0-NLP-ML"})

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🏥 {CHATBOT_NAME} - Hospital Guidance Chatbot")
    print(f"{'='*60}")
    print("✅ NLP Enabled - Natural Language Understanding")
    print("✅ ML Enabled - Intelligent Classification")
    print("✅ 50+ Symptoms Supported")
    print(f"{'='*60}\n")
    
    app.run(debug=True, port=5000)