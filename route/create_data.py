#!/usr/bin/env python3
"""
ПРОСТОЙ генератор данных для обучения нейросети
"""

import pandas as pd
import numpy as np
import os

def create_training_data():
    print("🎲 Создание данных для обучения нейросети...")
    
    data = []
    
    # Создаем 2000 примеров (можно увеличить)
    for i in range(2000):
        # Случайные параметры движения
        speed = np.random.uniform(20, 100)    # скорость 20-100 км/ч
        slope = np.random.uniform(-10, 10)    # уклон -10% до +10%
        elevation = np.random.uniform(0, 500) # высота 0-500м
        acceleration = np.random.uniform(-3, 3) # ускорение
        progress = np.random.uniform(0, 1)    # прогресс маршрута 0-100%
        
        # ПРОСТАЯ ФИЗИЧЕСКАЯ МОДЕЛЬ РАСХОДА
        base_consumption = 8.0  # базовый расход
        
        # Влияние скорости (парабола - минимум около 60 км/ч)
        speed_effect = 0.08 * (speed - 60) ** 2 / 100
        
        # Влияние уклона
        slope_effect = 0.4 * abs(slope)
        
        # Влияние ускорения
        acceleration_effect = 0.5 * abs(acceleration)
        
        # Суммируем все эффекты
        fuel_consumption = (base_consumption + 
                          speed_effect + 
                          slope_effect + 
                          acceleration_effect)
        
        # Добавляем небольшую случайность (как в реальных данных)
        fuel_consumption += np.random.normal(0, 0.3)
        
        # Минимальный расход 4.0 л/100км
        fuel_consumption = max(4.0, fuel_consumption)
        
        # Сохраняем пример
        data.append([
            speed, slope, elevation, acceleration, progress, 
            round(fuel_consumption, 1)
        ])
    
    # Создаем DataFrame
    df = pd.DataFrame(data, columns=[
        'speed', 'slope', 'elevation', 'acceleration', 'progress', 'fuel_consumption'
    ])
    
    # Сохраняем в файл
    os.makedirs('training_data', exist_ok=True)
    filename = 'training_data/fuel_training_data.csv'
    df.to_csv(filename, index=False)
    
    print(f"✅ Создано {len(data)} примеров для обучения")
    print(f"📁 Файл: {filename}")
    
    # Показываем несколько примеров
    print("\n📋 Примеры данных:")
    print(df.head(8).to_string(index=False))
    
    return filename

if __name__ == "__main__":
    create_training_data()