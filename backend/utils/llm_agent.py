def llm_analysis(prediction, confidence, symptoms):
    prediction = prediction.strip()
    symptoms = symptoms.lower().strip()

    explanation_map = {
        "Cerumen_Impaction": "Earwax buildup detected in the ear canal.",
        "Normal": "No visible abnormality detected in the ear.",
        "Acute_Otitis_Media": "Signs of middle ear infection are present.",
        "Chronic_Otitis_Media": "Chronic infection or inflammation observed.",
        "Myringosclerosis": "Scarring or calcification of the eardrum detected."
    }

    advice_map = {
        "Cerumen_Impaction": "Use ear drops or consult a doctor for safe cleaning.",
        "Normal": "No treatment required. Maintain proper ear hygiene.",
        "Acute_Otitis_Media": "Consult an ENT specialist. Medication may be required.",
        "Chronic_Otitis_Media": "Seek medical attention. Long-term treatment may be needed.",
        "Myringosclerosis": "Consult a doctor for evaluation and monitoring."
    }

    explanation = explanation_map.get(prediction, "No detailed explanation available.")
    advice = advice_map.get(prediction, "Consult a medical professional for further guidance.")

    # 🔥 CORRECT RISK LOGIC
    risk_map = {
        "Normal": "Low",
        "Cerumen_Impaction": "Low",
        "Myringosclerosis": "Medium",
        "Acute_Otitis_Media": "High",
        "Chronic_Otitis_Media": "High"
    }

    risk = risk_map.get(prediction, "Medium")

    # 🔥 SYMPTOMS MODIFIER
    if "pain" in symptoms or "earache" in symptoms:
        risk = "High"

    if "discharge" in symptoms:
        risk = "High"

    if "hearing loss" in symptoms and risk == "Low":
        risk = "Medium"

    # 🔥 LOW CONFIDENCE CASE
    if confidence < 60:
        risk = "Uncertain"
        advice = "Model confidence is low. Please consult a medical professional."

    extra = ""
    if symptoms:
        extra = f"Reported symptoms: {symptoms}"

    return {
        "explanation": explanation,
        "risk": risk,
        "advice": advice,
        "extra": extra
    }