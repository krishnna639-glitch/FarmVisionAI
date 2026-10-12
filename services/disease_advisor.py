DISEASE_GUIDANCE = {
    "Potato___Early_blight": {
        "name": "Potato early blight",
        "symptoms": "Brown, target-like spots with concentric rings, usually on older leaves; yellowing and leaf drop may follow.",
        "treatment": (
            "Remove badly affected leaves and plant debris; do not compost diseased material. Keep foliage dry, water at the soil "
            "level, and improve spacing for airflow. Rotate potatoes and tomatoes away from the affected bed for at least 2-3 years. "
            "If disease is spreading, ask your local agricultural extension service about a fungicide registered for potatoes and "
            "follow its label exactly."
        ),
        "prevention": (
            "Use healthy seed potatoes, rotate crops, control volunteer plants, mulch to reduce soil splash, and avoid overhead "
            "watering. Inspect lower leaves regularly."
        ),
    },
    "Potato___Late_blight": {
        "name": "Potato late blight",
        "symptoms": "Water-soaked, rapidly enlarging dark lesions on leaves, sometimes with pale growth at lesion edges in humid weather; stems and tubers can also be affected.",
        "treatment": (
            "Act quickly: isolate the affected area, remove and safely dispose of infected plants and tubers, and avoid moving wet "
            "foliage through the crop. Late blight can spread rapidly. Contact a local agricultural extension service promptly for "
            "confirmation and advice on locally registered fungicides; use products only as their labels direct."
        ),
        "prevention": (
            "Plant certified seed and resistant varieties where available, avoid overhead irrigation, provide good airflow, remove "
            "volunteer potatoes and cull piles, and monitor crops closely during cool, wet weather."
        ),
    },
    "Potato___healthy": {
        "name": "Healthy potato",
        "symptoms": "The model classified the leaf image as healthy. Continue monitoring; a photo-based result cannot rule out every plant problem.",
        "treatment": (
            "No disease treatment is indicated by this result. Keep watering consistent, avoid waterlogging, and remove dead plant "
            "material. If symptoms develop or worsen, take clear photos and consult a local agricultural extension service."
        ),
        "prevention": (
            "Rotate crops, use healthy seed, maintain good airflow, water at the soil level, and inspect leaves regularly."
        ),
    },
    "Tomato__Target_Spot": {
        "name": "Tomato target spot",
        "symptoms": "Small dark-brown leaf spots that may develop concentric rings; lesions can enlarge and cause yellowing or leaf drop, and fruit may also be marked.",
        "treatment": (
            "Remove heavily affected leaves and clear plant debris. Water at the soil level, avoid handling wet plants, and improve "
            "airflow. Rotate away from tomatoes and related crops. If it continues to spread, ask a local agricultural extension "
            "service about diagnosis and fungicides registered for tomatoes; follow label directions and local regulations."
        ),
        "prevention": (
            "Use crop rotation, adequate plant spacing, clean tools, mulch to reduce soil splash, and avoid overhead irrigation. "
            "Inspect plants often, especially in warm, humid weather."
        ),
    },
    "Tomato__Tomato_mosaic_virus": {
        "name": "Tomato mosaic virus",
        "symptoms": "Leaves may show mottled light and dark green patterns, distortion, or reduced growth; fruit can ripen unevenly.",
        "treatment": (
            "There is no cure that removes the virus from an infected plant. Remove and dispose of affected plants; do not put them "
            "in a home compost pile. Wash hands and disinfect tools before working on healthy plants. Avoid tobacco use while "
            "handling plants, since tobacco products can carry related virus particles."
        ),
        "prevention": (
            "Use certified virus-free seed or transplants and resistant varieties where available. Clean tools and hands between "
            "plants, remove weeds and volunteer tomatoes, and avoid handling plants after touching tobacco."
        ),
    },
    "Tomato_Tomato_YellowLeaf_Curl_Virus": {
        "name": "Tomato yellow leaf curl virus",
        "symptoms": "New leaves may curl upward and turn yellow, plants may become stunted, and fruit set can be poor. Whiteflies commonly spread the virus.",
        "treatment": (
            "There is no cure for an infected plant. Remove and dispose of symptomatic plants to reduce sources of infection. "
            "Manage whiteflies using integrated methods and locally approved products; do not rely on insecticide alone, as it may "
            "not prevent virus transmission. Ask your local agricultural extension service for region-specific guidance."
        ),
        "prevention": (
            "Choose resistant varieties where available, use insect-proof netting for young plants, remove nearby weeds and volunteer "
            "hosts, monitor for whiteflies, and consider reflective mulch where appropriate. Avoid excessive nitrogen."
        ),
    },
}


def _normalize(value):
    return "".join(character.lower() for character in value if character.isalnum())


def _resolve_disease(value):
    normalized_value = _normalize(value)
    for disease in DISEASE_GUIDANCE:
        if normalized_value == _normalize(disease):
            return disease

    # The classifier's yellow-leaf-curl label uses extra underscores in some versions.
    if "tomato" in normalized_value and "yellowleafcurlvirus" in normalized_value:
        return "Tomato_Tomato_YellowLeaf_Curl_Virus"

    return None


def reply_to_disease_question(selected_disease, message):
    disease = _resolve_disease(selected_disease)
    if disease is None:
        normalized_message = _normalize(message)
        matches = [
            key for key in DISEASE_GUIDANCE
            if _normalize(key) in normalized_message
        ]
        if matches:
            disease = max(matches, key=len)
        elif "yellowleafcurlvirus" in normalized_message:
            disease = "Tomato_Tomato_YellowLeaf_Curl_Virus"

    if disease is None:
        disease_names = ", ".join(
            details["name"] for details in DISEASE_GUIDANCE.values()
        )
        return (
            "Select a disease from the list, or include its name in your message. "
            f"I can help with: {disease_names}."
        )

    guidance = DISEASE_GUIDANCE[disease]
    question = message.lower()

    if any(term in question for term in ("symptom", "look like", "identify", "sign")):
        answer = f"Symptoms to look for: {guidance['symptoms']}"
    elif any(term in question for term in ("prevent", "avoid", "stop spread")):
        answer = f"Prevention: {guidance['prevention']}"
    else:
        answer = f"Recommended next steps: {guidance['treatment']}"

    return (
        f"{guidance['name']}\n{answer}\n\n"
        "A photo-based prediction is not a definitive diagnosis. For severe or spreading damage, "
        "confirm with your local agricultural extension service. Follow local pesticide labels and regulations."
    )
