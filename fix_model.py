#!/usr/bin/env python3
"""
Создание модели в правильном месте
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def create_and_save_model():
    print("🔄 Создание нейросети в правильном месте...")
    
    # Создаем простые данные
    data = []
    for i in range(1000):
        speed = np.random.uniform(20, 100)
        slope = np.random.uniform(-10, 10)
        elevation = np.random.uniform(0, 500)
        acceleration = np.random.uniform(-3, 3)
        progress = np.random.uniform(0, 1)
        
        # Модель расхода
        base = 8.0
        speed_effect = 0.08 * (speed - 60) ** 2 / 100
        slope_effect = 0.4 * abs(slope)
        acceleration_effect = 0.5 * abs(acceleration)
        
        fuel = base + speed_effect + slope_effect + acceleration_effect
        fuel += np.random.normal(0, 0.3)
        fuel = max(4.0, fuel)
        
        data.append([speed, slope, elevation, acceleration, progress, round(fuel, 1)])
    
    # Обучаем модель
    df = pd.DataFrame(data, columns=['speed', 'slope', 'elevation', 'acceleration', 'progress', 'fuel'])
    
    X = df[['speed', 'slope', 'elevation', 'acceleration', 'progress']].values
    y = df['fuel'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = MLPRegressor(hidden_layer_sizes=(30, 15), max_iter=500, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Сохраняем в ПРАВИЛЬНОМ месте
    os.makedirs('models', exist_ok=True)
    model_path = 'models/fuel_predictor.pkl'
    
    model_data = {
        'model': model,
        'scaler': scaler
    }
    joblib.dump(model_data, model_path)
    
    print(f"✅ Модель сохранена: {os.path.abspath(model_path)}")
    
    # Проверяем
    if os.path.exists(model_path):
        print("✅ Файл существует и доступен!")
        return True
    else:
        print("❌ Файл не создался!")
        return False

if __name__ == "__main__":
    create_and_save_model()