from recommended_grade.scorer import StudentAnswerScorer

# Изначально переменная пуста, модель не занимает память при старте Docker
_scorer_instance = None

def get_scorer() -> StudentAnswerScorer:
    """
    Ленивая инициализация семантического скорера.
    Объект создаётся ровно один раз при первом обращении к расчёту оценок.
    """
    global _scorer_instance
    if _scorer_instance is None:
        print(" [Scorer] Первая фиксация вызова. Начинается ленивая загрузка SiameseRuBERT...")
        
        # Переносим твою оригинальную конфигурацию внутрь функции
        _scorer_instance = StudentAnswerScorer(
            model_dir="recommended_grade/models/siamese_rubert_s_128",
            weights={"w1": 0.78, "w2": 0.2, "w3": 0.02}
        )
        
        print(" ✓ [Scorer] Семантическая модель успешно загружена в память и готова к работе.")
    return _scorer_instance