import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class NeuralFuelPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def load_training_data(self, csv_file):
        """Загрузка данных из CSV файла"""
        print(f"📂 Загрузка данных из {csv_file}...")
        
        df = pd.read_csv(csv_file)
        
        # Признаки (что подаем на вход нейросети)
        X = df[['speed', 'slope', 'elevation', 'acceleration', 'progress']].values
        
        # Целевая переменная (что хотим предсказать)
        y = df['fuel_consumption'].values
        
        print(f"✅ Загружено {len(X)} примеров")
        print(f"   Признаки: скорость, уклон, высота, ускорение, прогресс")
        print(f"   Цель: расход топлива")
        
        return X, y
    
    def train_model(self, csv_file, test_size=0.2):
        """Обучение нейросети"""
        # Загружаем данные
        X, y = self.load_training_data(csv_file)
        
        # Разделяем на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Масштабируем данные (очень важно для нейросетей!)
        print("⚖️  Масштабирование данных...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Создаем нейросеть
        self.model = MLPRegressor(
            hidden_layer_sizes=(50, 25),  # Архитектура: 2 скрытых слоя
            activation='relu',           # Функция активации
            solver='adam',               # Алгоритм обучения
            max_iter=1000,               # Максимум итераций
            random_state=42,             # Для воспроизводимости
            learning_rate_init=0.001     # Скорость обучения
        )
        
        # Обучаем модель
        print("🧠 Начинаем обучение нейросети...")
        print("   Это займет 10-30 секунд...")
        
        self.model.fit(X_train_scaled, y_train)
        
        # Проверяем качество
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print("✅ Обучение завершено!")
        print(f"📊 Точность на обучающих данных: {train_score:.3f}")
        print(f"📈 Точность на тестовых данных: {test_score:.3f}")
        
        self.is_trained = True
        return True
    
    def predict(self, speed, slope, elevation=100, acceleration=0, progress=0.5):
        """Предсказание расхода для новых данных"""
        if not self.is_trained:
            raise Exception("Модель не обучена!")
        
        # Подготовка входных данных
        features = np.array([[speed, slope, elevation, acceleration, progress]])
        
        # Масштабирование
        features_scaled = self.scaler.transform(features)
        
        # Предсказание
        prediction = self.model.predict(features_scaled)[0]
        
        return round(prediction, 1)
    
    def save_model(self, filepath='models/fuel_model.pkl'):
        """Сохранение обученной модели"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Сохраняем и модель, и scaler
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, filepath)
        print(f"💾 Модель сохранена: {filepath}")
    
    def load_model(self, filepath='models/fuel_model.pkl'):
        """Загрузка обученной модели"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = True
            print(f"📂 Модель загружена: {filepath}")
            return True
        return False
    
    def test_predictions(self):
        """Тестирование модели на разных сценариях"""
        if not self.is_trained:
            print("❌ Модель не обучена!")
            return
        
        print("\n🧪 ТЕСТИРОВАНИЕ МОДЕЛИ:")
        print("=" * 50)
        
        test_cases = [
            [60, 0, "Ровная дорога"],
            [60, 5, "Подъем 5%"],
            [55, 5, "Подъем 5%, медленнее"],
            [70, 5, "Подъем 5%, быстрее"],
            [60, -3, "Спуск 3%"],
            [80, 0, "Скорость по трассе"],
            [40, 0, "Городская скорость"],
        ]
        
        for speed, slope, description in test_cases:
            prediction = self.predict(speed, slope)
            print(f"   {description}")
            print(f"   Скорость: {speed}км/ч, Уклон: {slope}%")
            print(f"   → Предсказанный расход: {prediction} л/100км\n")