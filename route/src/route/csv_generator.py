import csv
import os
import joblib
import numpy as np
from src.route.data_processor import DataProcessor
from src.route.elevation_calculator import ElevationCalculator
from src.route.fuel_calculator import FuelCalculator
from src.route.smart_speed_optimizer import SmartSpeedOptimizer

class CSVGenerator:
    def __init__(self, use_neural_network=True):
        self.data_processor = DataProcessor()
        self.elevation_calculator = ElevationCalculator()
        self.fuel_calculator = FuelCalculator()
        self.speed_optimizer = SmartSpeedOptimizer()
        
        # Загрузка обученной нейросети
        self.use_neural_network = use_neural_network
        self.neural_model = None
        self.neural_scaler = None
        
        if use_neural_network:
            self.load_neural_model()
    
    def load_neural_model(self):
        """Загрузка обученной нейросети - выводится ОДИН РАЗ"""
        # Пробуем разные возможные пути
        possible_paths = [
            'models/fuel_predictor.pkl',           # относительно корня
            '../models/fuel_predictor.pkl',        # из папки src/route
            '../../models/fuel_predictor.pkl',     # из глубоких папок
            './models/fuel_predictor.pkl',         # текущая директория
        ]
        
        for model_path in possible_paths:
            if os.path.exists(model_path):
                try:
                    model_data = joblib.load(model_path)
                    self.neural_model = model_data['model']
                    self.neural_scaler = model_data['scaler']
                    self.use_neural_network = True
                    return True  # Успешно загружено
                except Exception as e:
                    print(f"❌ Ошибка загрузки {model_path}: {e}")
                    break
        
        # Если не удалось загрузить
        self.use_neural_network = False
        return False
    
    def predict_fuel_consumption(self, speed, slope, elevation=100, acceleration=0, progress=0.5):
        """Предсказание расхода с использованием нейросети или физической модели"""
        if self.use_neural_network and self.neural_model is not None:
            # Используем нейросеть БЕЗ вывода сообщений
            try:
                features = np.array([[speed, slope, elevation, acceleration, progress]])
                features_scaled = self.neural_scaler.transform(features)
                prediction = self.neural_model.predict(features_scaled)[0]
                return max(4.0, prediction)
            except Exception as e:
                # Тихо переключаемся на физическую модель
                pass
        
        # Используем физическую модель как запасной вариант
        return self.fuel_calculator.calculate_fuel_consumption_physical(speed, slope)
    
    def create_csv_file(self, points, route_length_km, filename='маршрут_с_скоростями.csv'):
        """Создание CSV файла с использованием нейросети"""
        print("💾 Создание CSV файла с ИИ-оптимизацией...")
        
        # Загружаем нейросеть (ОДИН РАЗ в начале)
        neural_loaded = self.load_neural_model()
        if neural_loaded:
            print("✅ Нейросеть загружена для предсказания расхода")
        else:
            print("💡 Используется физическая модель расхода")
        
        # Получаем данные о высотах и уклонах
        elevations, slopes = self.elevation_calculator.get_elevation_data(points)
        
        # Генерируем текущие скорости
        current_speeds = self.data_processor.generate_realistic_speeds(len(points), route_length_km)
        
        # Рассчитываем оптимальные скорости
        optimal_speeds, energy_savings = self.speed_optimizer.calculate_smart_speed_profile(
            slopes, current_speeds, route_length_km
        )
        
        # Расчет расходов с использованием НЕЙРОСЕТИ
        current_consumptions = []
        optimal_consumptions = []
        
        if neural_loaded:
            print("🧠 Расчет расходов с помощью нейросети...")
        else:
            print("📐 Расчет расходов по физической модели...")
        
        for i, (current_speed, optimal_speed, slope, elevation) in enumerate(zip(
            current_speeds, optimal_speeds, slopes, elevations)):
            
            progress = i / len(points)
            
            # Используем нейросеть для предсказания!
            current_consumption = self.predict_fuel_consumption(
                current_speed, slope, elevation, 0, progress
            )
            optimal_consumption = self.predict_fuel_consumption(
                optimal_speed, slope, elevation, 0, progress
            )
            
            current_consumptions.append(current_consumption)
            optimal_consumptions.append(optimal_consumption)
        
        # Создаем папку если её нет
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'shirota', 'dolgota', 'elevation', 'slope_percent', 
                'current_speed', 'current_fuel_consumption',
                'smart_optimal_speed', 'smart_optimal_fuel_consumption', 
                'fuel_saving', 'energy_saving'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            
            for i, point in enumerate(points):
                fuel_saving = current_consumptions[i] - optimal_consumptions[i]
                
                writer.writerow({
                    'shirota': f"{point['lat']:.6f}",
                    'dolgota': f"{point['lon']:.6f}",
                    'elevation': f"{elevations[i]:.1f}",
                    'slope_percent': f"{slopes[i]:.2f}",
                    'current_speed': f"{current_speeds[i]}",
                    'current_fuel_consumption': f"{current_consumptions[i]:.1f}",
                    'smart_optimal_speed': f"{optimal_speeds[i]}",
                    'smart_optimal_fuel_consumption': f"{optimal_consumptions[i]:.1f}",
                    'fuel_saving': f"{fuel_saving:.1f}",
                    'energy_saving': f"{energy_savings[i]:.1f}"
                })
        
        print(f"✅ CSV файл с ИИ-оптимизацией создан: {filename}")
        
        # Статистика - ИСПРАВЛЕННЫЙ ВЫЗОВ!
        self._print_smart_statistics(current_speeds, optimal_speeds, current_consumptions, 
                                optimal_consumptions, route_length_km)
        
        return optimal_speeds, optimal_consumptions
    
    def _print_smart_statistics(self, current_speeds, optimal_speeds, current_consumptions, 
                              optimal_consumptions, route_length_km):
        """Вывод статистики с ПРАВИЛЬНЫМ расчетом экономии"""
        avg_current_speed = sum(current_speeds) / len(current_speeds)
        avg_optimal_speed = sum(optimal_speeds) / len(optimal_speeds)
        avg_current_consumption = sum(current_consumptions) / len(current_consumptions)
        avg_optimal_consumption = sum(optimal_consumptions) / len(optimal_consumptions)
        
        # ПРАВИЛЬНЫЙ расчет экономии
        # Средний расход в л/100км переводим в литры на ВЕСЬ маршрут
        current_fuel_total = (avg_current_consumption * route_length_km) / 100
        optimal_fuel_total = (avg_optimal_consumption * route_length_km) / 100
        total_fuel_saved = current_fuel_total - optimal_fuel_total
        
        # Процент экономии
        saving_percentage = (total_fuel_saved / current_fuel_total) * 100 if current_fuel_total > 0 else 0
        
        # Экономия на 100км (для сравнения)
        fuel_saving_per_100km = avg_current_consumption - avg_optimal_consumption
        
        print(f"\n🤖 СТАТИСТИКА С ИСКУССТВЕННЫМ ИНТЕЛЛЕКТОМ:")
        print(f"   🧠 Используется: {'НЕЙРОСЕТЬ' if self.use_neural_network else 'ФИЗИЧЕСКАЯ МОДЕЛЬ'}")
        print(f"   🚗 Ваша средняя скорость: {avg_current_speed:.1f} км/ч")
        print(f"   🎯 Рекомендуемая скорость: {avg_optimal_speed:.1f} км/ч")
        print(f"   ⛽ Ваш средний расход: {avg_current_consumption:.1f} л/100км")
        print(f"   💰 Рекомендуемый расход: {avg_optimal_consumption:.1f} л/100км")
        print(f"   🔥 ЭКОНОМИЯ: {saving_percentage:.1f}%")
        print(f"   💵 Сэкономлено на маршруте: {total_fuel_saved:.2f} л")
        print(f"   📏 Экономия на 100км: {fuel_saving_per_100km:.2f} л")
        
        # Дополнительная информация
        print(f"\n   📊 Детали маршрута:")
        print(f"   📏 Длина маршрута: {route_length_km:.1f} км")
        print(f"   ⛽ Всего топлива (ваш стиль): {current_fuel_total:.2f} л")
        print(f"   ⛽ Всего топлива (оптимально): {optimal_fuel_total:.2f} л")
        
        # Денежная экономия (примерно 50 руб/литр)
        money_saved = total_fuel_saved * 50
        print(f"   💰 Сэкономлено денег: {money_saved:.0f} руб")
    