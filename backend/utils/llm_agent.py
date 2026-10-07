def llm_analysis(prediction, confidence, symptoms):
    prediction = prediction.strip().replace("_", " ")
    symptoms_text = symptoms.strip()
    symptoms_lower = symptoms_text.lower()

    explanation_map = {
        "Cerumen Impaction": (
            "The image is most consistent with cerumen impaction, meaning a buildup "
            "of earwax in the ear canal. The appearance can partially or completely "
            "obscure the eardrum."
        ),
        "Normal": (
            "The image appears consistent with a normal ear appearance. No obvious "
            "abnormality from the five classes supported by this model was detected."
        ),
        "Acute Otitis Media": (
            "The image is most consistent with acute otitis media, an acute inflammatory "
            "condition of the middle ear. Otoscopic findings can include changes in the "
            "appearance or position of the eardrum."
        ),
        "Chronic Otitis Media": (
            "The image is most consistent with chronic otitis media, a persistent or "
            "recurrent inflammatory condition of the middle ear. Chronic disease can "
            "be associated with long-standing changes to the eardrum."
        ),
        "Myringosclerosis": (
            "The image is most consistent with myringosclerosis, which refers to "
            "whitish scar-like or calcified changes involving the eardrum. Clinical "
            "assessment is needed to determine its significance."
        ),
    }

    advice_map = {
        "Cerumen Impaction": (
            "Avoid inserting cotton buds or other objects into the ear. If the ear feels "
            "blocked, painful, or hearing is reduced, seek professional evaluation for "
            "safe assessment and removal when appropriate."
        ),
        "Normal": (
            "No specific treatment is suggested by this AI result. Continue routine ear "
            "care and seek medical advice if you have persistent pain, discharge, hearing "
            "changes, fever, or other concerning symptoms."
        ),
        "Acute Otitis Media": (
            "Arrange a medical evaluation, particularly if there is significant pain, "
            "fever, discharge, or worsening symptoms. A healthcare professional can "
            "decide whether treatment is needed."
        ),
        "Chronic Otitis Media": (
            "Arrange an ENT or healthcare evaluation, especially for persistent discharge, "
            "hearing changes, recurrent symptoms, or pain. Long-standing ear disease may "
            "require follow-up."
        ),
        "Myringosclerosis": (
            "Discuss the finding with a healthcare professional if it is new, associated "
            "with hearing changes, pain, discharge, or other symptoms. Clinical examination "
            "can determine whether further monitoring is needed."
        ),
    }

    risk_map = {
        "Normal": "Low",
        "Cerumen Impaction": "Low",
        "Myringosclerosis": "Medium",
        "Acute Otitis Media": "High",
        "Chronic Otitis Media": "High",
    }

    explanation = explanation_map.get(
        prediction,
        "The model returned a result, but a detailed explanation is not available for this class."
    )
    advice = advice_map.get(
        prediction,
        "Please consult a qualified healthcare professional for clinical interpretation."
    )
    risk = risk_map.get(prediction, "Medium")

    symptom_flags = []
    if "pain" in symptoms_lower or "earache" in symptoms_lower:
        symptom_flags.append("ear pain")
        risk = "High"
    if "discharge" in symptoms_lower or "fluid" in symptoms_lower:
        symptom_flags.append("ear discharge"
                             )
        risk = "High"
    if "hearing loss" in symptoms_lower or "hearing difficulty" in symptoms_lower:
        symptom_flags.append("hearing changes")
        if risk == "Low":
            risk = "Medium"
    if "fever" in symptoms_lower:
        symptom_flags.append("fever")
        risk = "High"

    confidence_note = (
        "The model confidence is relatively low, so the prediction should be treated "
        "with extra caution."
        if confidence < 60
        else "The model reports high confidence for this image, but confidence does not "
             "mean clinical certainty."
        if confidence >= 90
        else "The model reports moderate confidence; clinical assessment is still important."
    )

    if confidence < 60:
        risk = "Uncertain"
        advice = (
            "The model confidence is low. Do not rely on this result for a medical decision; "
            "please consult a qualified healthcare professional."
        )

    extra_parts = [confidence_note]
    if symptom_flags:
        extra_parts.append(
            "Reported symptoms relevant to this assessment: " + ", ".join(symptom_flags) + "."
        )
    if symptoms_text:
        extra_parts.append(
            "The symptoms are provided as context only; the image model does not diagnose "
            "symptoms independently."
        )

    return {
        "explanation": explanation,
        "risk": risk,
        "advice": advice,
        "extra": " ".join(extra_parts),
    }
