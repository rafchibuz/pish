#!/usr/bin/env python3
"""
ГЛАВНЫЙ файл для обучения нейросети
Просто запустите: python train_model.py
"""

import os
import sys

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ml.fuel_predictor import NeuralFuelPredictor

def main():
    print("🎓 ОБУЧЕНИЕ НЕЙРОСЕТИ ДЛЯ ПРЕДСКАЗАНИЯ РАСХОДА ТОПЛИВА")
    print("=" * 60)
    
    # Шаг 1: Создаем данные (если их нет)
    data_file = 'training_data/fuel_training_data.csv'
    if not os.path.exists(data_file):
        print("1. 📊 Создаем данные для обучения...")
        from create_data import create_training_data
        data_file = create_training_data()
    else:
        print(f"1. 📊 Данные уже существуют: {data_file}")
    
    # Шаг 2: Создаем и обучаем модель
    print("\n2. 🧠 Создаем нейросеть...")
    predictor = NeuralFuelPredictor()
    
    print("\n3. 🏋️  Начинаем обучение...")
    success = predictor.train_model(data_file)
    
    if success:
        # Шаг 3: Сохраняем модель
        print("\n4. 💾 Сохраняем обученную модель...")
        predictor.save_model()
        
        # Шаг 4: Тестируем модель
        print("\n5. 🧪 Тестируем предсказания...")
        predictor.test_predictions()
        
        print("\n🎉 ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("💡 Теперь можно использовать модель в основной программе")
    else:
        print("\n💥 Ошибка обучения модели")

if __name__ == "__main__":
    main()