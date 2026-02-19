"""
Custom mappings for questions that don't match well with TF-IDF
Updated with correct IDs from the database
"""

# Common question patterns and their correct FAQ IDs
CUSTOM_MAPPINGS = {
    # School fees related
    "how much is school fees": 29,        # ID 29: "How much are the school fees?"
    "school fees amount": 29,
    "tuition fee": 29,
    "fees for freshers": 29,
    "payment for school": 29,
    "school fee": 29,
    "fees payment": 29,
    "how much are school fees": 29,
    "amount of school fees": 29,

    # School fees payment
    "how to pay school fees": 27,          # ID 27: "How do I pay my school fees?"
    "pay school fees": 27,
    "school fees payment method": 27,
    "where to pay fees": 27,

    # Installment payment
    "pay in installments": 28,             # ID 28: "Can I pay my school fees in installments?"
    "installment payment": 28,
    "part payment": 28,
    "pay in parts": 28,

    # Second choice related
    "second choice": 7,                    # ID 7: "Does LAUTECH accept second-choice candidates?"
    "second choice jamb": 7,
    "can i choose lautech as second choice": 7,
    "does lautech accept second choice": 7,
    "second choice candidate": 7,
    "jamb second choice": 7,
    "accept second choice": 7,

    # Verification documents
    "verification documents": 15,           # ID 15: "What documents are needed for the verification exercise?"
    "documents needed for verification": 15,
    "screening documents": 15,
    "what to bring for verification": 15,
    "verification exercise": 15,
    "documents for screening": 15,
    "required documents": 15,

    # Best places to live
    "best place to live": 54,               # ID 54: "Which area is the quietest for academic-focused students?"
    "where to stay": 54,
    "good area to live": 54,
    "safe place to live": 54,
    "best area for students": 54,
    "where should i live": 54,
    "accommodation area": 54,
    "quiet area": 54,
    "area for students": 54,

    # Library hours / reading
    "library hours": 24,                    # ID 24: "What is the procedure for library registration?"
    "library reading time": 24,
    "when can i use library": 24,
    "library opening time": 24,
    "library schedule": 24,
    "library reading hours": 24,
    "how to register for library": 24,
    "library registration": 24,

    # Best reading spots
    "best place to read": 41,               # ID 41: "What is the best place to read in LAUTECH?"
    "where to read": 41,
    "reading spot": 41,
    "study area": 41,
    "place to study": 41,

    # Cultists / Security
    "cultists": 40,                         # ID 40: "Are there cultists in LAUTECH?"
    "cult on campus": 40,
    "cultism": 40,
    "campus cult": 40,
    "are there cultists": 40,
    "cult activities": 40,
    "campus security": 40,
    "is it safe": 39,                        # ID 39: "Which areas around LAUTECH are the safest to live in?"
    "safe areas": 39,
    "secure areas": 39,

    # Cut off mark for medicine
    "cut off mark medicine": 8,              # ID 8: "What is the cut-off mark for my course?"
    "medicine cut off": 8,
    "cut off for medicine": 8,
    "medicine cut-off mark": 8,
    "cutoff for medicine": 8,

    # Post UTME
    "post utme": 9,                          # ID 9: "Is there a Post-UTME exam?"
    "post utme form": 9,
    "pume": 9,
    "post utme screening": 9,
    "when is post utme": 9,
    "post utme registration": 10,             # ID 10: "How do I apply for the Post-UTME screening?"
    "how to apply for post utme": 10,

    # Hostel accommodation
    "hostel": 32,                            # ID 32: "Does the school provide hostel accommodation?"
    "hostel accommodation": 32,
    "school hostel": 32,
    "on campus hostel": 32,
    "accommodation": 32,
    "where to live": 54,                      # ID 54 for best area

    # Cheapest lodges
    "cheapest lodge": 43,                     # ID 43: "Which area has the cheapest lodges around LAUTECH?"
    "cheap accommodation": 43,
    "affordable area": 43,

    # Electricity
    "best electricity": 38,                   # ID 38: "Which area around LAUTECH has the most stable electricity?"
    "stable electricity": 38,
    "light area": 38,
    "power supply": 38,

    # Food
    "best food": 37,                          # ID 37: "Which restaurant sells the best food around LAUTECH?"
    "restaurant": 37,
    "where to eat": 37,
    "food around campus": 37,
    "cheap food": 51,                         # ID 51: "Where can I get affordable food around LAUTECH?"
    "affordable food": 51,

    # Transport
    "transport fare": 46,                     # ID 46: "What is the average transport fare from major areas to LAUTECH?"
    "fare to school": 46,
    "how much to school": 46,
    "transport cost": 46,

    # Bikes on campus
    "bikes on campus": 47,                    # ID 47: "Are bikes allowed on campus?"
    "motorcycle on campus": 47,
    "okada on campus": 47,

    # Water supply
    "best water": 48,                         # ID 48: "Which area has the best water supply?"
    "water supply": 48,
    "area with water": 48,

    # Internet
    "fast internet": 50,                      # ID 50: "Which area is best for fast internet connections?"
    "wifi area": 50,
    "internet connection": 50,

    # Phone/laptop repair
    "phone repair": 57,                       # ID 57: "Where can I repair my laptop or phone?"
    "laptop repair": 57,
    "repair phone": 57,
    "fix my phone": 57,

    # Add to CUSTOM_MAPPINGS dictionary:

    # Location
    "where is lautech": 2,                    # ID 2: "Where is LAUTECH located?"
    "lautech location": 2,
    "address of lautech": 2,
    "lautech situated": 2,

    # Cut off (short queries)
    "cut off": 8,                              # ID 8: "What is the cut-off mark for my course?"
    "cutoff": 8,
    "cut-off": 8,
    "jamb cut off": 8,
    "cut off mark": 8,

    # Hostel (short queries)
    "hostel": 32,                               # ID 32: "Does the school provide hostel accommodation?"
    "hostels": 32,
    "school hostel": 32,
    "accommodation": 32,
    "where to sleep": 32,
    "place to stay": 54,                         # ID 54 for best area

    # Medicine with typos
    "medcine": 11,                               # ID 11: Medicine requirements
    "medecine": 11,
    "medicin": 11,
    "medical": 11,
    "doctor": 11,

# Add to CUSTOM_MAPPINGS:

# School / general queries
"school": 2,                          # ID 2: "Where is LAUTECH located?" (most general)
"about lautech": 1,                    # ID 1: Full meaning
"tell me about lautech": 1,
"lautech info": 1,
"university": 2,
"campus": 2,


    # Repair with partial matches
    "repair": 57,                                # ID 57: "Where can I repair my laptop or phone?"
    "fix": 57,
    "broken": 57,
    "laptop repair": 57,
    "phone repair": 57,
    "technician": 57,

    # Engineering
    "engineer": 19,                              # ID 19: "What degrees are awarded (e.g., BTech vs BSc)?"
    "engineering": 19,
    "btech": 19,
    "b.tech": 19,
}

# Keywords to boost for specific categories
CATEGORY_KEYWORDS = {
    "fees": ["fee", "fees", "pay", "payment", "tuition", "money", "cost", "amount", "school fee"],
    "admission": ["admission", "admit", "jamb", "utme", "post-utme", "cutoff", "cut-off", "mark", "score", "requirement"],
    "accommodation": ["hostel", "accommodation", "lodge", "room", "live", "stay", "area", "place", "where"],
    "academics": ["course", "program", "department", "faculty", "degree", "btech", "bsc", "study"],
    "security": ["security", "safe", "cult", "cultist", "danger", "protect", "campus"],
    "library": ["library", "read", "reading", "book", "study", "hours"],
    "medicine": ["medicine", "med", "medical", "doctor", "clinical"],
    "food": ["food", "restaurant", "eat", "shawarma", "rice", "meal"],
    "transport": ["transport", "fare", "bike", "bus", "car", "okada"],
    "electricity": ["electricity", "light", "power", "solar"],
}

def get_custom_match(question):
    """
    Check if question matches any custom mapping
    Returns dict with faq_id and confidence or None
    """
    question_lower = question.lower().strip()

    # Check exact matches in CUSTOM_MAPPINGS
    for pattern, faq_id in CUSTOM_MAPPINGS.items():
        if pattern in question_lower:
            return {
                'faq_id': faq_id,
                'confidence': 0.95,
                'match_type': 'custom_exact',
                'matched_by': 'custom_mapping'
            }

    # Check for partial matches (if question contains key terms)
    words = set(question_lower.split())

    # Look for category matches
    best_category = None
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if any(keyword in word for word in words))
        if matches > best_score:
            best_score = matches
            best_category = category

    # Map categories to specific FAQ IDs
    category_to_faq = {
        "fees": 29,           # How much are the school fees?
        "accommodation": 54,   # Which area is the quietest?
        "security": 40,        # Are there cultists?
        "library": 24,         # Library registration procedure
        "medicine": 8,         # Medicine cut-off
        "food": 37,            # Best food
        "transport": 46,       # Transport fare
        "electricity": 38,     # Best electricity
    }

    if best_category and best_score >= 2:  # At least 2 keyword matches
        return {
            'faq_id': category_to_faq.get(best_category),
            'confidence': 0.85,
            'match_type': 'custom_category',
            'matched_by': 'category_mapping'
        }

    return None