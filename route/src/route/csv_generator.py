import csv
import os
from src.route.data_processor import DataProcessor
from src.route.elevation_calculator import ElevationCalculator
from src.route.fuel_calculator import FuelCalculator

class CSVGenerator:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.elevation_calculator = ElevationCalculator()
        self.fuel_calculator = FuelCalculator()
    
    def create_csv_file(self, points, route_length_km, filename='маршрут_с_скоростями.csv'):
        """Создание CSV файла с координатами, скоростями, высотами, уклонами и оптимальными параметрами"""
        print("💾 Создание расширенного CSV файла...")
        
        # Получаем данные о высотах и уклонах
        elevations, slopes = self.elevation_calculator.get_elevation_data(points)
        
        # Генерируем текущие скорости
        current_speeds = self.data_processor.generate_realistic_speeds(len(points), route_length_km)
        
        # Рассчитываем оптимальные скорости и расходы
        segment_distances = [route_length_km / len(points)] * len(points)
        optimal_speeds, optimal_consumptions = self.fuel_calculator.calculate_route_optimal_speeds(slopes, segment_distances)
        
        # Рассчитываем текущий расход
        current_consumptions = []
        for i, (speed, slope) in enumerate(zip(current_speeds, slopes)):
            consumption = self.fuel_calculator.calculate_fuel_consumption_physical(speed, slope)
            current_consumptions.append(consumption)
        
        # Создаем папку если её нет
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Расширенные колонки
            fieldnames = [
                'shirota', 'dolgota', 'elevation', 'slope_percent', 
                'current_speed', 'current_fuel_consumption',
                'optimal_speed', 'optimal_fuel_consumption',
                'fuel_saving'
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
                    'optimal_speed': f"{optimal_speeds[i]}",
                    'optimal_fuel_consumption': f"{optimal_consumptions[i]:.1f}",
                    'fuel_saving': f"{fuel_saving:.1f}"
                })
        
        print(f"✅ Расширенный CSV файл создан: {filename}")
        
        # Статистика
        self._print_fuel_statistics(current_speeds, optimal_speeds, current_consumptions, optimal_consumptions)
        
        return optimal_speeds, optimal_consumptions
    
    def _print_fuel_statistics(self, current_speeds, optimal_speeds, current_consumptions, optimal_consumptions):
        """Вывод статистики по расходу"""
        avg_current_speed = sum(current_speeds) / len(current_speeds)
        avg_optimal_speed = sum(optimal_speeds) / len(optimal_speeds)
        avg_current_consumption = sum(current_consumptions) / len(current_consumptions)
        avg_optimal_consumption = sum(optimal_consumptions) / len(optimal_consumptions)
        total_saving = sum(current_consumptions) - sum(optimal_consumptions)
        
        print(f"\n📊 СТАТИСТИКА ОПТИМИЗАЦИИ РАСХОДА:")
        print(f"   🚗 Текущая средняя скорость: {avg_current_speed:.1f} км/ч")
        print(f"   🎯 Оптимальная средняя скорость: {avg_optimal_speed:.1f} км/ч")
        print(f"   ⛽ Текущий расход: {avg_current_consumption:.1f} л/100км")
        print(f"   💰 Оптимальный расход: {avg_optimal_consumption:.1f} л/100км")
        print(f"   💵 Экономия: {total_saving:.1f} л на 100км")
        print(f"   📈 Процент экономии: {(total_saving/avg_current_consumption)*100:.1f}%")