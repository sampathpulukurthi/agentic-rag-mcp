"""Seed data utilities for bootstrapping the knowledge base."""

from __future__ import annotations

from typing import Dict, List

FAQ_TEXT = """Question 1: What is the first step before building a machine learning model?
Answer 1: Understand the problem, define the objective, and identify the right metrics for evaluation.

Question 2: How important is data cleaning in ML?
Answer 2: Extremely important. Clean data improves model performance and reduces the chance of misleading results.

Question 3: Should I normalize or standardize my data?
Answer 3: Yes, especially for models sensitive to feature scales like SVMs, KNN, and neural networks.

Question 4: When should I use feature engineering?
Answer 4: Always consider it. Well-crafted features often yield better results than complex models.

Question 5: How to handle missing values?
Answer 5: Use imputation techniques like mean/median imputation, or model-based imputation depending on the context.

Question 6: Should I balance my dataset for classification tasks?
Answer 6: Yes, especially if the classes are imbalanced. Techniques include resampling, SMOTE, and class-weighting.

Question 7: How do I select features for my model?
Answer 7: Use domain knowledge, correlation analysis, or techniques like Recursive Feature Elimination or SHAP values.

Question 8: Is it good to use all features available?
Answer 8: Not always. Irrelevant or redundant features can reduce performance and increase overfitting.

Question 9: How do I avoid overfitting?
Answer 9: Use techniques like cross-validation, regularization, pruning (for trees), and dropout (for neural nets).

Question 10: Why is cross-validation important?
Answer 10: It provides a more reliable estimate of model performance by reducing bias from a single train-test split.

Question 11: What’s a good train-test split ratio?
Answer 11: Common ratios are 80/20 or 70/30, but use cross-validation for more robust evaluation.

Question 12: Should I tune hyperparameters?
Answer 12: Yes. Use grid search, random search, or Bayesian optimization to improve model performance.

Question 13: What’s the difference between training and validation sets?
Answer 13: Training set trains the model, validation set tunes hyperparameters, and test set evaluates final performance.

Question 14: How do I know if my model is underfitting?
Answer 14: It performs poorly on both training and test sets, indicating it hasn’t learned patterns well.

Question 15: What are signs of overfitting?
Answer 15: High accuracy on training data but poor generalization to test or validation data.

Question 16: Is ensemble modeling useful?
Answer 16: Yes. Ensembles like Random Forests or Gradient Boosting often outperform individual models.

Question 17: When should I use deep learning?
Answer 17: Use it when you have large datasets, complex patterns, or tasks like image and text processing.

Question 18: What is data leakage and how to avoid it?
Answer 18: Data leakage is using future or target-related information during training. Avoid by carefully splitting and preprocessing.

Question 19: How do I measure model performance?
Answer 19: Choose appropriate metrics: accuracy, precision, recall, F1, ROC-AUC for classification; RMSE, MAE for regression.

Question 20: Why is model interpretability important?
Answer 20: It builds trust, helps debug, and ensures compliance—especially important in high-stakes domains like healthcare.
"""


def parse_faq(text: str = FAQ_TEXT) -> List[Dict[str, str]]:
    """Parse the FAQ text into structured entries."""

    entries: List[Dict[str, str]] = []
    blocks = [block.strip() for block in text.strip().split("\n\n") if block.strip()]

    for idx, block in enumerate(blocks, start=1):
        lines = block.split("\n")
        if len(lines) != 2:
            continue

        question = lines[0].split(":", 1)[1].strip()
        answer = lines[1].split(":", 1)[1].strip()
        entries.append(
            {
                "id": f"faq-{idx}",
                "question": question,
                "answer": answer,
                "text": f"Question: {question}\nAnswer: {answer}",
            }
        )

    return entries
