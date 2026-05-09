import random
from typing import List
from modules.questions.models import Question

def generate_balanced_tests(
    questions: List[Question], 
    num_tests: int, 
    questions_per_test: int
) -> List[dict]:
    # Приводим все веса к float сразу, чтобы не было конфликтов типов
    total_pool_sum = sum(float(q.complexity_score or 0) for q in questions)
    ideal_avg_test = (total_pool_sum / len(questions)) * questions_per_test

    # Подготовка пула
    random.shuffle(questions)
    sorted_questions = sorted(questions, key=lambda q: float(q.complexity_score or 0), reverse=True)

    tickets = [{"questions": [], "sum": 0.0} for i in range(num_tests)]
    available_pool = list(sorted_questions)

    # Распределение
    for _ in range(questions_per_test):
        for _ in range(num_tests):
            if not available_pool:
                available_pool = list(sorted_questions)

            # Выбираем билет с минимальной суммой
            current_ticket = min(tickets, key=lambda t: (len(t["questions"]), t["sum"]))

            candidates_indices = [
                i for i, q in enumerate(available_pool)
                if q.id_question not in [quest.id_question for quest in current_ticket["questions"]]
            ]

            if not candidates_indices:
                raise ValueError("Недостаточно уникальных вопросов")

            # Выбираем из топ-2 для вариативности
            top_slice_indices = candidates_indices[:2] 
            chosen_idx = random.choice(top_slice_indices)
            
            # Предварительный расчет сложности
            q_complexity = float(available_pool[chosen_idx].complexity_score or 0)
            projected_sum = current_ticket["sum"] + q_complexity

            # Проверка порога 0.5
            if abs(projected_sum - ideal_avg_test) > 0.5 and chosen_idx != candidates_indices[0]:
                chosen_idx = candidates_indices[0]
            
            candidate = available_pool.pop(chosen_idx)

            current_ticket["questions"].append(candidate)
            current_ticket["sum"] += float(candidate.complexity_score or 0)

    # Рандом номеров
    test_numbers = list(range(1, num_tests + 1))
    random.shuffle(test_numbers)
    for i in range(num_tests):
        tickets[i]["test_number"] = test_numbers[i]

    tickets.sort(key=lambda x: x["test_number"])
    return tickets