def calculate_disorder_scores(responses, question_bank):
    
    disorder_raw = {}
    disorder_max = {}
    disorder_severity = {}

    # print(responses)
    # print(question_bank)

   
    for qid, info in question_bank.items():
        weight = info.get('weight', 1)
        for disorder in info['disorders']:
            disorder_raw.setdefault(disorder, 0)
            disorder_max.setdefault(disorder, 0)
            
            disorder_max[disorder] += 5 * weight

   
    for resp in responses:
        qid = resp['question_id']
        ans = int(resp['answer'])
        info = question_bank.get(qid)
        if not info:
            continue
        weight = info.get('weight', 1)
        for disorder in info['disorders']:
            disorder_raw[disorder] += ans * weight

   
    for disorder, raw_score in disorder_raw.items():
        max_score = disorder_max.get(disorder, 1)
        percent = (raw_score / max_score) * 100

        if percent <= 20:
            sev = 'none'
        elif percent <= 40:
            sev = 'mild'
        elif percent <= 60:
            sev = 'moderate'
        elif percent <= 80:
            sev = 'moderately severe'
        else:
            sev = 'severe'

        disorder_severity[disorder] = sev


    # print(disorder_raw)
    # print(disorder_severity)
    return disorder_raw, disorder_severity


