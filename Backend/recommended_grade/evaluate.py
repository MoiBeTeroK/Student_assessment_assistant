 
"""
evaluate.py — оценка формулы S^w1 * C^w2 * H^w3 + grid search по весам.

Запуск:
    python evaluate.py

Что делает:
    1. Считает S, C, H для каждого примера из test.csv (один раз)
    2. Перебирает все комбинации весов с шагом WEIGHT_STEP
    3. Находит лучшие веса по точности
    4. Выводит полный отчёт для лучших весов
    5. Сохраняет результаты в results/
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
)
from Backend.recommended_grade.scorer import StudentAnswerScorer, compute_C_raw, compute_H

MODEL_DIR   = "models/siamese_rubert_s_128"
TEST_PATH   = "datasets/test.csv"
OUTPUT_DIR  = "results"

WEIGHT_STEP = 0.01

GRADE_THRESHOLDS = [
    (0.875, 5),
    (0.625, 4),
    (0.375, 3),
    (0.0,   2),
]
 


def read_csv(path: str) -> pd.DataFrame:
    for enc in ["utf-8-sig", "utf-8", "cp1251"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось прочитать: {path}")


def generate_weight_combinations(step: float) -> list:
    """
    Все комбинации (w1, w2, w3) с шагом step,
    где w1 + w2 + w3 = 1.0 и каждый вес >= step.
    """
    combos = []
    n = round(1 / step)
    for i in range(1, n):
        for j in range(1, n - i):
            k = n - i - j
            if k >= 1:
                combos.append((
                    round(i * step, 2),
                    round(j * step, 2),
                    round(k * step, 2),
                ))
    return combos


def scores_to_grades(scores: np.ndarray) -> np.ndarray:
    """Числовой score → оценка 2/3/4/5 для массива."""
    grades = np.full(len(scores), 2, dtype=int)
    for threshold, grade in sorted(GRADE_THRESHOLDS, reverse=False):
        grades[scores >= threshold] = grade
    return grades


def apply_weights(
    s_arr: np.ndarray,
    c_arr: np.ndarray,
    h_arr: np.ndarray,
    w1: float, w2: float, w3: float,
) -> np.ndarray:
    """Считает итоговые оценки для заданных весов — без обращения к модели."""
    scores = (np.maximum(s_arr, 1e-9) ** w1 *
              np.maximum(c_arr, 1e-9) ** w2 *
              np.maximum(h_arr, 1e-9) ** w3)
    return scores_to_grades(scores)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

     
    print("=" * 60)
    print("1. Загрузка данных")
    print("=" * 60)

    REQUIRED = ["Вопрос", "Эталонный ответ преподавателя", "Ответ студента", "Оценка"]
    test_df = read_csv(TEST_PATH).dropna(subset=REQUIRED).reset_index(drop=True)
    print(f"Тестовых примеров: {len(test_df)}")

     
    print("\n" + "=" * 60)
    print("2. Загрузка модели")
    print("=" * 60)

    scorer = StudentAnswerScorer(
        model_dir  = MODEL_DIR,
        max_length = 128
    )

     
    print("\n" + "=" * 60)
    print("3. Вычисление S, C, H для каждого примера")
    print("=" * 60)

    s_list, c_list, h_list, true_grades = [], [], [], []
    total = len(test_df)

    for i, row in test_df.iterrows():
        if i % 100 == 0:
            print(f"  Обработано: {i}/{total}")

        question  = str(row["Вопрос"])
        reference = str(row["Эталонный ответ преподавателя"])
        student   = str(row["Ответ студента"])

        result = scorer.score(question, reference, student)

        s_list.append(result["S"])
        c_list.append(result["C"])
        h_list.append(result["H"])
        true_grades.append(int(row["Оценка"]))

    s_arr = np.array(s_list)
    c_arr = np.array(c_list)
    h_arr = np.array(h_list)
    true_arr = np.array(true_grades)

    print(f"\nГотово. S: {s_arr.mean():.3f} | C: {c_arr.mean():.3f} | H: {h_arr.mean():.3f}")

     
    print("\n" + "=" * 60)
    print("4. Grid search по весам")
    print("=" * 60)

    combos = generate_weight_combinations(WEIGHT_STEP)
    print(f"Комбинаций весов: {len(combos)} (шаг={WEIGHT_STEP})")

    grid_results = []
    for w1, w2, w3 in combos:
        pred = apply_weights(s_arr, c_arr, h_arr, w1, w2, w3)
        acc  = accuracy_score(true_arr, pred)
        mae  = mean_absolute_error(true_arr, pred)
        acc1 = float(np.mean(np.abs(true_arr - pred) <= 1))
        grid_results.append({
            "w1": w1, "w2": w2, "w3": w3,
            "accuracy": round(acc, 4),
            "acc_pm1":  round(acc1, 4),
            "mae":      round(mae, 4),
        })

    grid_df = pd.DataFrame(grid_results).sort_values("accuracy", ascending=False)

    print("\nТоп-10 комбинаций весов по точности:")
    print(f"{'w1':>5} {'w2':>5} {'w3':>5} | {'Accuracy':>10} {'Acc±1':>8} {'MAE':>8}")
    print("-" * 50)
    for _, r in grid_df.head(10).iterrows():
        print(f"{r['w1']:>5.2f} {r['w2']:>5.2f} {r['w3']:>5.2f} | "
              f"{r['accuracy']:>10.4f} {r['acc_pm1']:>8.4f} {r['mae']:>8.4f}")

     
    best = grid_df.iloc[0]
    best_w1, best_w2, best_w3 = best["w1"], best["w2"], best["w3"]
    print(f"\n★ Лучшие веса: S^{best_w1} × C^{best_w2} × H^{best_w3}")
    print(f"  Accuracy: {best['accuracy']:.4f} ({best['accuracy']*100:.1f}%)")
    print(f"  Acc ±1:   {best['acc_pm1']:.4f} ({best['acc_pm1']*100:.1f}%)")
    print(f"  MAE:      {best['mae']:.4f}")

     
    print("\n" + "=" * 60)
    print("5. Полный отчёт для лучших весов")
    print("=" * 60)

    best_pred = apply_weights(s_arr, c_arr, h_arr, best_w1, best_w2, best_w3)

    print("\nПо оценкам (2/3/4/5):")
    print(classification_report(true_arr, best_pred, digits=4))

    print("Матрица ошибок (строки=реальные, столбцы=предсказанные):")
    cm = confusion_matrix(true_arr, best_pred, labels=[2, 3, 4, 5])
    cm_df = pd.DataFrame(
        cm,
        index=["real_2", "real_3", "real_4", "real_5"],
        columns=["pred_2", "pred_3", "pred_4", "pred_5"],
    )
    print(cm_df.to_string())

     
    print("\n" + "=" * 60)
    print("6. Статистика компонентов по оценкам")
    print("=" * 60)

    comp_df = pd.DataFrame({"true_grade": true_arr, "S": s_arr, "C": c_arr, "H": h_arr})
    for grade in [2, 3, 4, 5]:
        sub = comp_df[comp_df["true_grade"] == grade]
        print(f"\nОценка {grade} (n={len(sub)}):")
        print(f"  S  mean={sub['S'].mean():.3f}  std={sub['S'].std():.3f}")
        print(f"  C  mean={sub['C'].mean():.3f}  std={sub['C'].std():.3f}")
        print(f"  H  mean={sub['H'].mean():.3f}  std={sub['H'].std():.3f}")

     
    print("\n" + "=" * 60)
    print("7. Корреляция компонентов с оценкой преподавателя")
    print("=" * 60)

    true_float = true_arr.astype(float)
    for name, arr in [("S", s_arr), ("C", c_arr), ("H", h_arr)]:
        corr = np.corrcoef(arr, true_float)[0, 1]
        print(f"  {name}: Pearson = {corr:.4f}")

     
    print("\n" + "=" * 60)
    print("8. Сохранение результатов")
    print("=" * 60)

     
    grid_df.to_csv(f"{OUTPUT_DIR}/grid_search.csv", index=False, encoding="utf-8-sig")
    print(f"Grid search : {OUTPUT_DIR}/grid_search.csv")

     
    best_scores = (np.maximum(s_arr, 1e-9) ** best_w1 *
                   np.maximum(c_arr, 1e-9) ** best_w2 *
                   np.maximum(h_arr, 1e-9) ** best_w3)

    detail_df = pd.DataFrame({
        "true_grade": true_arr,
        "pred_grade": best_pred,
        "score":      best_scores.round(4),
        "S":          s_arr,
        "C":          c_arr,
        "H":          h_arr,
        "question":   test_df["Вопрос"].str[:80],
        "student":    test_df["Ответ студента"].str[:100],
    })
    detail_df.to_csv(f"{OUTPUT_DIR}/evaluation_best.csv", index=False, encoding="utf-8-sig")
    print(f"Детали      : {OUTPUT_DIR}/evaluation_best.csv")

     
    summary = {
        "best_weights":  {"w1": best_w1, "w2": best_w2, "w3": best_w3},
        "n_test":        int(len(test_df)),
        "accuracy":      float(best["accuracy"]),
        "acc_pm1":       float(best["acc_pm1"]),
        "mae":           float(best["mae"]),
        "weight_step":   WEIGHT_STEP,
        "n_combinations": len(combos),
        "pearson_S":     round(float(np.corrcoef(s_arr, true_float)[0, 1]), 4),
        "pearson_C":     round(float(np.corrcoef(c_arr, true_float)[0, 1]), 4),
        "pearson_H":     round(float(np.corrcoef(h_arr, true_float)[0, 1]), 4),
    }
    with open(f"{OUTPUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Сводка      : {OUTPUT_DIR}/summary.json")


if __name__ == "__main__":
    main()