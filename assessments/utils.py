def calculate_disorder_scores(responses, question_bank):
    disorder_raw = {}
    disorder_max = {}

    # Dynamically calculate max scores based on questions' weights
    for entry in responses:
        qid = int(entry['question_id'])
        answer = int(entry['answer'])
        question = question_bank[qid]

        if question["reverse_scored"]:
            answer = 3 - answer  # assuming 0–3 scale

        # For each disorder affected by the question, add to raw score
        for disorder in question["disorders"]:
            weight = question["weight"]
            disorder_raw[disorder] = disorder_raw.get(disorder, 0) + answer * weight

            # Calculate max possible score for each disorder (3 * weight per question)
            disorder_max[disorder] = disorder_max.get(disorder, 0) + 3 * weight  # Max score for this question

    disorder_severity = {}

    # For each disorder, calculate the percentage of the max score
    for disorder, score in disorder_raw.items():
        max_score = disorder_max[disorder]  # dynamically calculated max score
        percent = (score / max_score) * 100

        # Severity scale: customize these cutoffs for your specific assessment
        if percent <= 20:
            severity = 'none'
        elif percent <= 40:
            severity = 'mild'
        elif percent <= 60:
            severity = 'moderate'
        elif percent <= 80:
            severity = 'moderately severe'
        else:
            severity = 'severe'

        disorder_severity[disorder] = severity

    return disorder_raw, disorder_severity
