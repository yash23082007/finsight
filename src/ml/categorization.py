import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pickle
import os

class ExpenseCategorizer:
    def __init__(self, model_path="models/categorizer.pkl"):
        self.model_path = model_path
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
            ('clf', LogisticRegression(random_state=42, max_iter=1000))
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

        X = train_df['description']
        y = train_df['category']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
        
        self.metrics = {
            'accuracy': acc,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        self.is_trained = True
        self.save_model()
        return True, "Model trained successfully."

    def predict(self, description: str) -> str:
        if not self.is_trained:
            self.load_model()
        if not self.is_trained:
            return "Unknown"
        return self.pipeline.predict([description])[0]

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
