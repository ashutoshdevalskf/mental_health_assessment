def calculate_disorder_scores(responses, question_bank):
    raw_scores = {}

    for response in responses:
        question_id = int(response['question_id'])
        answer = int(response['answer'])
        q_info = question_bank[question_id]

        score = 4 - answer if q_info['reverse_scored'] else answer
        score *= q_info['weight']

        for disorder in q_info['disorders']:
            raw_scores[disorder] = raw_scores.get(disorder, 0) + score

           # Determine severity thresholds (example)
    severity_scores = {}
    for disorder, score in raw_scores.items():
        if score >= 18:
            severity = 'Severe'
        elif score >= 12:
            severity = 'Moderate'
        elif score >= 6:
            severity = 'Mild'
        else:
            severity = 'None'
        severity_scores[disorder] = severity

    return raw_scores, severity_scores
