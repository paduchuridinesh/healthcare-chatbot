"""
MediGuide - Hospital Guidance Chatbot
Flask API with NLP and ML Integration
"""

import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_engine import TriageBot

app = Flask(__name__)
# TODO before go-live: lock CORS to your hospital domain, e.g.:
# CORS(app, origins=["https://yourhospital.com"])
CORS(app)

SESSION_MAX = 500  # max concurrent sessions kept in RAM

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

    # --- Session cleanup: remove sessions idle for more than 30 minutes ---
    cutoff = time.time() - 1800
    expired = [k for k, v in sessions.items() if v.get("last_active", 0) < cutoff]
    for k in expired:
        del sessions[k]

    # --- Session cap: evict oldest if limit exceeded ---
    if len(sessions) > SESSION_MAX:
        oldest = sorted(sessions.items(), key=lambda x: x[1].get("last_active", 0))
        for k, _ in oldest[:len(sessions) - SESSION_MAX]:
            del sessions[k]

    # Initialize session if new user
    if user_id not in sessions:
        sessions[user_id] = {
            "step": "START",
            "symptom": None,
            "duration": None,
            "severity": None,
            "severity_score": None,
            "answers": [],
            "disclaimer_shown": False,
            "last_active": time.time()
        }

    # Refresh activity timestamp on every message
    sessions[user_id]["last_active"] = time.time()

    state = sessions[user_id]

    # === EMERGENCY CHECK (HIGHEST PRIORITY) ===
    # Full scan at START; focused high-confidence scan during follow-up to avoid false triggers
    if state["step"] == "START":
        is_emergency, emergency_msg = bot.detect_emergency(message)
    else:
        is_emergency, emergency_msg = bot.detect_emergency_critical(message)
    if is_emergency:
        sessions[user_id] = {
            "step": "COMPLETED",
            "symptom": None,
            "duration": None,
            "severity": None,
            "severity_score": None,
            "answers": [],
            "disclaimer_shown": True,
            "last_active": time.time()
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
                    f"How long have you been experiencing this symptom?")
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
                "reply": "I couldn't quite catch that. Could you tell me how long you've been experiencing this symptom? For example, you could say the number of hours or days.",
                "options": []
            })
        
        state["duration"] = duration_info
        state["step"] = "SEVERITY"
        
        reply = "Thank you. How would you describe the severity of your symptom?"
        return jsonify({"reply": reply, "options": []})

    # === STEP 3: SEVERITY ===
    if state["step"] == "SEVERITY":
        severity_data = bot.extract_severity(message)
        
        if severity_data is not None:
            severity_label, severity_score = severity_data
            state["severity"] = severity_label
            state["severity_score"] = severity_score
            state["step"] = "FOLLOW_UP_Q1"
            
            # Start with first follow-up question
            symptom = state["symptom"]
            questions = bot.symptoms_data[symptom]["questions"]
            
            reply = f"Understood, thank you. Now, I have a few more questions to better assess your situation.\n\n{questions[0]}"
            return jsonify({"reply": reply, "options": [], "question_num": 1, "question_total": len(questions)})
        else:
            return jsonify({
                "reply": "I didn't quite catch that. Could you describe how severe it is? You can use words like mild, moderate, or severe, or give a number from 1 to 10.",
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
                    "reply": f"Could you please answer with Yes or No?\n\n{current_question}",
                    "options": []
                })
        
        # Save the validated answer
        state["answers"].append(message)
        
        # Calculate next question index
        current_q_num = len(state["answers"])
        
        # Check if more questions remain
        if current_q_num < len(questions):
            state["step"] = f"FOLLOW_UP_Q{current_q_num + 1}"
            next_question = questions[current_q_num]
            return jsonify({"reply": next_question, "options": [], "question_num": current_q_num + 1, "question_total": len(questions)})
        
        # === FINAL CLASSIFICATION USING ML ===
        else:
            # Only pass answers from yes/no questions as red-flag signals
            YES_NO_TRIGGERS = ["are you", "do you", "can you", "have you", "did you", "is there", "is it"]
            yes_no_answers = [
                state["answers"][i]
                for i, q in enumerate(questions)
                if i < len(state["answers"]) and "?" in q
                and any(t in q.lower() for t in YES_NO_TRIGGERS)
            ]

            result = bot.classify_issue_ml(
                symptom=symptom,
                duration_info=state["duration"],
                severity_data=(state["severity"], state["severity_score"]),
                follow_up_answers=yes_no_answers
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
    
    # Set debug=False before deploying to production
    app.run(debug=False, port=5000)