"""
Обучение Siamese RuBERT для компонента S формулы S^w1 * C^w2 * H^w3.

Идея:
    - Два одинаковых RuBERT кодируют эталон и ответ студента отдельно
    - Учим их так, чтобы косинус между векторами соответствовал оценке
    - S = cosine_similarity(эмбеддинг эталона, эмбеддинг ответа)

Таргет для обучения:
    оценка 2 → S_target = 0.25
    оценка 3 → S_target = 0.50
    оценка 4 → S_target = 0.75
    оценка 5 → S_target = 1.00
    формула: S_target = (оценка - 1) / 4

Loss: CosineSimilarityLoss
    loss = MSE(cosine(эталон, ответ), S_target)
    Модель учится делать эмбеддинги так, чтобы угол между ними
    отражал качество ответа студента.
"""

import os
import json
import random
import warnings
warnings.filterwarnings("ignore")

os.environ["WANDB_DISABLED"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
TRAIN_PATH   = "datasets/train.csv"
TEST_PATH    = "datasets/test.csv"
MODEL_NAME   = "DeepPavlov/rubert-base-cased"
OUTPUT_DIR   = "models/siamese_rubert_s_128"
SEED         = 42

LR           = 2e-5
EPOCHS       = 5
MAX_LENGTH   = 128   
BATCH_TRAIN  = 2     
BATCH_EVAL   = 4   
GRAD_ACCUM   = 16   
WEIGHT_DECAY = 0.01
WARMUP_RATIO = 0.1
MAX_GRAD     = 1.0
DROPOUT      = 0.1
PATIENCE     = 3

GRADE_THRESHOLDS = [
    (0.875, 5),
    (0.625, 4),
    (0.375, 3),
    (0.0,   2),
]

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def grade_to_s(grade) -> float:
    """Оценка 2/3/4/5 → S_target ∈ [0.25, 1.0]"""
    return (float(grade) - 1) / 4


def s_to_grade(s: float) -> int:
    """S ∈ [0, 1] → оценка 2/3/4/5"""
    for threshold, grade in GRADE_THRESHOLDS:
        if s >= threshold:
            return grade
    return 2


def read_csv(path: str) -> pd.DataFrame:
    for enc in ["utf-8-sig", "utf-8", "cp1251"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось прочитать: {path}")


 
 
 
FILLER_WORDS = [
    "ну", "вот", "это", "типа", "как бы", "значит",
    "в общем", "короче", "то есть", "собственно",
]
 
def augment(text: str, p_drop: float = 0.05, p_fill: float = 0.05) -> str:
    words = text.split()
    if not words:
        return text
    result = []
    for w in words:
        if random.random() < p_drop:
            continue
        if random.random() < p_fill:
            result.append(random.choice(FILLER_WORDS))
        result.append(w)
    return " ".join(result) if result else text


class SiameseDataset(Dataset):
    """
    Возвращает два отдельно токенизированных текста:
        - reference: эталонный ответ преподавателя
        - student:   ответ студента
    и S_target — целевое косинусное сходство.

    Вопрос добавляется к обоим текстам как контекст:
        "[вопрос] [SEP] [текст ответа]"
    """

    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer,
        max_length: int = 128,
        is_training: bool = False,
    ):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.is_training = is_training

    def __len__(self):
        return len(self.df)

    def _tokenize(self, text: str) -> dict:
        enc = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "token_type_ids": enc.get(
                "token_type_ids",
                torch.zeros(self.max_length, dtype=torch.long)
            ).squeeze(0),
        }

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        question  = str(row["Вопрос"])
        reference = str(row["Эталонный ответ преподавателя"])
        student   = str(row["Ответ студента"])
        s_target  = grade_to_s(row["Оценка"])

         
        ref_text = question + " [SEP] " + reference
        stu_text = question + " [SEP] " + (augment(student) if self.is_training else student)

        ref_enc = self._tokenize(ref_text)
        stu_enc = self._tokenize(stu_text)

        return {
            "ref_input_ids":      ref_enc["input_ids"],
            "ref_attention_mask": ref_enc["attention_mask"],
            "ref_token_type_ids": ref_enc["token_type_ids"],
            "stu_input_ids":      stu_enc["input_ids"],
            "stu_attention_mask": stu_enc["attention_mask"],
            "stu_token_type_ids": stu_enc["token_type_ids"],
            "s_target":           torch.tensor(s_target, dtype=torch.float),
        }


 
 
 
class SiameseRuBERT(nn.Module):
    """
    Один RuBERT используется дважды (веса общие) —
    сначала кодирует эталон, потом ответ студента.
    S = cosine_similarity(embed_ref, embed_stu)

    Эмбеддинг = Mean Pooling по всем не-паддинговым токенам.
    Mean Pooling устойчивее чем [CLS] для sentence similarity задач.
    """

    def __init__(self, model_name: str, dropout: float = 0.1):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.bert.gradient_checkpointing_enable()   
        self.dropout = nn.Dropout(dropout)

    def mean_pool(self, token_embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Mean pooling — среднее по не-паддинговым токенам."""
        mask = attention_mask.unsqueeze(-1).float()           
        summed = (token_embeddings * mask).sum(dim=1)         
        count  = mask.sum(dim=1).clamp(min=1e-9)              
        return summed / count                                  

    def encode(self, input_ids, attention_mask, token_type_ids=None) -> torch.Tensor:
        """Кодирует один текст → нормализованный эмбеддинг."""
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )
        pooled = self.mean_pool(outputs.last_hidden_state, attention_mask)
        pooled = self.dropout(pooled)
         
        return F.normalize(pooled, p=2, dim=-1)

    def forward(
        self,
        ref_input_ids,   ref_attention_mask,   ref_token_type_ids,
        stu_input_ids,   stu_attention_mask,   stu_token_type_ids,
    ) -> torch.Tensor:
        """Возвращает косинусное сходство для каждой пары в батче."""
        ref_emb = self.encode(ref_input_ids, ref_attention_mask, ref_token_type_ids)
        stu_emb = self.encode(stu_input_ids, stu_attention_mask, stu_token_type_ids)
         
        cosine = (ref_emb * stu_emb).sum(dim=-1)   
         
        return (cosine + 1) / 2


 
 
 
def evaluate(model, loader, device) -> dict:
    model.eval()
    all_s_pred, all_s_true = [], []

    with torch.no_grad():
        for batch in loader:
            s_pred = model(
                batch["ref_input_ids"].to(device),
                batch["ref_attention_mask"].to(device),
                batch["ref_token_type_ids"].to(device),
                batch["stu_input_ids"].to(device),
                batch["stu_attention_mask"].to(device),
                batch["stu_token_type_ids"].to(device),
            )
            all_s_pred.extend(s_pred.cpu().numpy())
            all_s_true.extend(batch["s_target"].numpy())

    s_pred = np.array(all_s_pred)
    s_true = np.array(all_s_true)

    mae  = np.mean(np.abs(s_pred - s_true))
    rmse = np.sqrt(np.mean((s_pred - s_true) ** 2))

     
    pred_grades = [s_to_grade(s) for s in s_pred]
    true_grades = [round(s * 4 + 1) for s in s_true]
    grade_acc = np.mean(np.array(pred_grades) == np.array(true_grades))

     
    if s_pred.std() > 0 and s_true.std() > 0:
        pearson = np.corrcoef(s_pred, s_true)[0, 1]
    else:
        pearson = 0.0

    return {
        "mae":       round(float(mae), 4),
        "rmse":      round(float(rmse), 4),
        "grade_acc": round(float(grade_acc), 4),
        "pearson":   round(float(pearson), 4),
    }


 
 
 
def main():
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Устройство: {device}\n")

     
    print("=" * 60)
    print("1. Загрузка данных")
    print("=" * 60)

    REQUIRED = ["Вопрос", "Эталонный ответ преподавателя", "Ответ студента", "Оценка"]

    train_full = read_csv(TRAIN_PATH).dropna(subset=REQUIRED)
    test_df    = read_csv(TEST_PATH).dropna(subset=REQUIRED)

    print(f"Train+Val: {len(train_full)} | Test: {len(test_df)}")
    print("Оценки (train):")
    print(train_full["Оценка"].value_counts().sort_index().to_string())

     
    unique_q = train_full["Вопрос"].unique()
    train_q, val_q = train_test_split(unique_q, test_size=0.1, random_state=SEED)

    train_df = train_full[train_full["Вопрос"].isin(train_q)].reset_index(drop=True)
    val_df   = train_full[train_full["Вопрос"].isin(val_q)].reset_index(drop=True)

    print(f"\nTrain: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

     
    print("\n" + "=" * 60)
    print("2. Подготовка датасетов")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = SiameseDataset(train_df, tokenizer, MAX_LENGTH, is_training=True)
    val_dataset   = SiameseDataset(val_df,   tokenizer, MAX_LENGTH, is_training=False)
    test_dataset  = SiameseDataset(test_df,  tokenizer, MAX_LENGTH, is_training=False)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_TRAIN, shuffle=True,  num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_dataset,   batch_size=BATCH_EVAL,  shuffle=False, num_workers=2, pin_memory=True)
    test_loader  = DataLoader(test_dataset,  batch_size=BATCH_EVAL,  shuffle=False, num_workers=2, pin_memory=True)

    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_dataset)}")

     
    print("\n" + "=" * 60)
    print("3. Загрузка модели")
    print("=" * 60)

    model = SiameseRuBERT(MODEL_NAME, dropout=DROPOUT).to(device)
    total = sum(p.numel() for p in model.parameters())
    print(f"Модель: {MODEL_NAME}")
    print(f"Параметров: {total:,}")

     
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LR,
        weight_decay=WEIGHT_DECAY,
    )

    total_steps  = (len(train_loader) // GRAD_ACCUM) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

     
    criterion = nn.MSELoss()

     
    print("\n" + "=" * 60)
    print("4. Обучение")
    print("=" * 60)
    print(f"Эпох: {EPOCHS} | LR: {LR} | Batch: {BATCH_TRAIN} | GradAccum: {GRAD_ACCUM}")
    print(f"Всего шагов: {total_steps} | Warmup: {warmup_steps}\n")

    best_val_mae = float("inf")
    best_epoch   = 0
    patience_cnt = 0

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        optimizer.zero_grad()

        for step, batch in enumerate(train_loader, 1):
            s_pred = model(
                batch["ref_input_ids"].to(device),
                batch["ref_attention_mask"].to(device),
                batch["ref_token_type_ids"].to(device),
                batch["stu_input_ids"].to(device),
                batch["stu_attention_mask"].to(device),
                batch["stu_token_type_ids"].to(device),
            )
            s_true = batch["s_target"].to(device)

            loss = criterion(s_pred, s_true) / GRAD_ACCUM
            loss.backward()
            total_loss += loss.item() * GRAD_ACCUM

            if step % GRAD_ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        avg_loss    = total_loss / len(train_loader)
        torch.cuda.empty_cache()
        val_metrics = evaluate(model, val_loader, device)

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"Loss: {avg_loss:.4f} | "
            f"Val MAE: {val_metrics['mae']:.4f} | "
            f"Val RMSE: {val_metrics['rmse']:.4f} | "
            f"Val Acc: {val_metrics['grade_acc']:.4f} | "
            f"Pearson: {val_metrics['pearson']:.4f}"
        )

        if val_metrics["mae"] < best_val_mae:
            best_val_mae = val_metrics["mae"]
            best_epoch   = epoch
            patience_cnt = 0
            torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, "best_model.pt"))
            print(f"  ✓ Лучший Val MAE: {best_val_mae:.4f} — сохранено")
        else:
            patience_cnt += 1
            if patience_cnt >= PATIENCE:
                print(f"\nEarly stopping. Лучшая эпоха: {best_epoch}")
                break

     
    print("\n" + "=" * 60)
    print("5. Финальная оценка на тесте")
    print("=" * 60)

    model.load_state_dict(
        torch.load(os.path.join(OUTPUT_DIR, "best_model.pt"), map_location=device)
    )
    test_metrics = evaluate(model, test_loader, device)

    print(f"\nTest MAE:       {test_metrics['mae']:.4f}")
    print(f"Test RMSE:      {test_metrics['rmse']:.4f}")
    print(f"Test Grade Acc: {test_metrics['grade_acc']:.4f}")
    print(f"Test Pearson:   {test_metrics['pearson']:.4f}")

     
    from sklearn.metrics import classification_report
    model.eval()
    all_pred_grades, all_true_grades = [], []

    with torch.no_grad():
        for batch in test_loader:
            s_pred = model(
                batch["ref_input_ids"].to(device),
                batch["ref_attention_mask"].to(device),
                batch["ref_token_type_ids"].to(device),
                batch["stu_input_ids"].to(device),
                batch["stu_attention_mask"].to(device),
                batch["stu_token_type_ids"].to(device),
            ).cpu().numpy()
            s_true = batch["s_target"].numpy()

            all_pred_grades.extend([s_to_grade(s) for s in s_pred])
            all_true_grades.extend([round(s * 4 + 1) for s in s_true])

    print("\nПо оценкам (2/3/4/5):")
    print(classification_report(all_true_grades, all_pred_grades, digits=4))

     
    print("\n" + "=" * 60)
    print("6. Сохранение")
    print("=" * 60)

    tokenizer.save_pretrained(OUTPUT_DIR)

    config = {
        "model_name":      MODEL_NAME,
        "architecture":    "SiameseRuBERT",
        "max_length":      MAX_LENGTH,
        "pooling":         "mean",
        "s_formula":       "cosine_similarity(embed_ref, embed_stu) mapped to [0,1]",
        "s_normalization": "(grade - 1) / 4",
        "grade_thresholds": GRADE_THRESHOLDS,
        "score_formula":   "S^w1 * C^w2 * H^w3",
        "weights":         {"w1": 0.5, "w2": 0.3, "w3": 0.2},
        "best_val_mae":    best_val_mae,
        "best_epoch":      best_epoch,
    }
    with open(os.path.join(OUTPUT_DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"Модель сохранена в: {OUTPUT_DIR}")
    print(f"Лучшая эпоха: {best_epoch} | Val MAE: {best_val_mae:.4f}")


if __name__ == "__main__":
    main()