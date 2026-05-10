from typing import List, Dict
from . import models

def calculate_group_statistics(results: List[models.ExamResult]) -> Dict:
    total = len(results)
    if total == 0: return {}

    sum_sim = sum_term = sum_coh = 0.0
    total_questions = 0
    total_diff = 0.0
    matches_ai = 0
    
    question_map = {}
    ai_dist = {i: 0 for i in range(2, 6)}
    final_dist = {i: 0 for i in range(2, 6)}

    for res in results:
        rec_val = float(res.rec_grade or 0)
        fin_val = float(res.final_grade or 0)
        
        if int(round(rec_val)) == int(round(fin_val)):
            matches_ai += 1
        total_diff += (fin_val - rec_val)
        
        ai_dist[int(round(rec_val))] = ai_dist.get(int(round(rec_val)), 0) + 1
        final_dist[int(round(fin_val))] = final_dist.get(int(round(fin_val)), 0) + 1
        
        if res.analitics_data:
            for q in res.analitics_data:
                audio_data = q.get('audio', {})
                q_id = audio_data.get('id_question')
                q_text = audio_data.get('question_text', "Текст не найден")
                
                s = q.get('similarity', 0)
                sum_sim += s
                sum_term += q.get('term_coverage', 0)
                sum_coh += q.get('speech_coherence', 0)
                total_questions += 1
                
                if q_id:
                    if q_id not in question_map:
                        question_map[q_id] = {"scores": [], "text": q_text}
                    question_map[q_id]["scores"].append(s)

    worst_question = None
    if question_map:
        avg_scores = {qid: sum(v["scores"])/len(v["scores"]) for qid, v in question_map.items()}
        worst_qid = min(avg_scores, key=avg_scores.get)
        worst_question = {
            "id": worst_qid,
            "question_text": question_map[worst_qid]["text"],
            "avg_similarity": round(avg_scores[worst_qid], 2)
        }

    return {
        "total_exams": total,
        "ai_agreement_rate": round((matches_ai / total) * 100, 2),
        "avg_grade_difference": round(total_diff / total, 2),
        "metrics": {
            "avg_similarity": round(sum_sim / total_questions, 2) if total_questions else 0,
            "avg_term_coverage": round(sum_term / total_questions, 2) if total_questions else 0,
            "avg_speech_coherence": round(sum_coh / total_questions, 2) if total_questions else 0,
        },
        "worst_question": worst_question,
        "distribution": {"ai_grades": ai_dist, "final_grades": final_dist}
    }