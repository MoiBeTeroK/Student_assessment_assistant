from recommended_grade.scorer import StudentAnswerScorer

scorer = StudentAnswerScorer(
    model_dir="recommended_grade/models/siamese_rubert_s_128",
    weights={"w1": 0.78, "w2": 0.2, "w3": 0.02}
)