import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pickle
import os

class ExpenseCategorizer:
    def __init__(self, model_path="models/categorizer.pkl"):
        self.model_path = model_path
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
            ('clf', LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced"))
        ])
        self.is_trained = False
        self.metrics = {}
        
        # Ensure models dir exists
        os.makedirs(os.path.dirname(self.model_path) if os.path.dirname(self.model_path) else ".", exist_ok=True)

    def train(self, df: pd.DataFrame):
        """Train the model on descriptions to predict categories."""
        # Only use expenses
        train_df = df[df['type'] == 'Expense'].copy()
        if len(train_df) < 50:
            return False, "Insufficient data for training (need at least 50 expense records)."

        X = train_df['description'].fillna("").astype(str).str.replace(r"\b\d+\b", " ", regex=True)
        y = train_df['category']
        groups = train_df.get("merchant", train_df["description"]).fillna(train_df["description"]).astype(str).str.lower()

        if y.nunique() < 2:
            return False, "Insufficient category diversity for training."
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, test_idx = next(splitter.split(X, y, groups=groups))
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
        class_precision, class_recall, class_f1, class_labels = precision_recall_fscore_support(
            y_test, y_pred, average=None, zero_division=0
        )
        
        self.metrics = {
            'accuracy': acc,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'per_class': {
                str(label): {
                    "precision": float(class_precision[index]),
                    "recall": float(class_recall[index]),
                    "f1": float(class_f1[index]),
                }
                for index, label in enumerate(class_labels)
            },
        }
        
        self.is_trained = True
        self.save_model()
        return True, "Model trained successfully."

    def predict(self, description: str) -> str:
        if not self.is_trained:
            self.load_model()
        if not self.is_trained:
            return "Unknown"
        probabilities = self.pipeline.predict_proba([description])[0]
        if probabilities.max() < 0.55:
            return "Needs review"
        return self.pipeline.classes_[probabilities.argmax()]

    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump({'pipeline': self.pipeline, 'metrics': self.metrics}, f)

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.pipeline = data['pipeline']
                self.metrics = data.get('metrics', {})
                self.is_trained = True
