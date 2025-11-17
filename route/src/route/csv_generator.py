import csv
import os
from src.route.data_processor import DataProcessor
from src.route.elevation_calculator import ElevationCalculator
from src.route.fuel_calculator import FuelCalculator
from src.route.smart_speed_optimizer import SmartSpeedOptimizer  # ДОБАВИТЬ

class CSVGenerator:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.elevation_calculator = ElevationCalculator()
        self.fuel_calculator = FuelCalculator()
        self.speed_optimizer = SmartSpeedOptimizer()  # ДОБАВИТЬ
    
    def create_csv_file(self, points, route_length_km, filename='маршрут_с_скоростями.csv'):
        """Создание CSV файла с умной оптимизацией"""
        print("💾 Создание CSV файла с умной оптимизацией...")
        
        # Получаем данные о высотах и уклонах
        elevations, slopes = self.elevation_calculator.get_elevation_data(points)
        
        # Генерируем текущие скорости (как едет водитель)
        current_speeds = self.data_processor.generate_realistic_speeds(len(points), route_length_km)
        
        # РАСЧЕТ УМНЫХ ОПТИМАЛЬНЫХ СКОРОСТЕЙ
        print("🧠 Расчет умных оптимальных скоростей...")
        optimal_speeds, energy_savings = self.speed_optimizer.calculate_smart_speed_profile(
            slopes, current_speeds, route_length_km
        )
        
        # Расчет расходов
        current_consumptions = []
        optimal_consumptions = []
        
        for i, (current_speed, optimal_speed, slope) in enumerate(zip(current_speeds, optimal_speeds, slopes)):
            current_consumption = self.fuel_calculator.calculate_fuel_consumption_physical(current_speed, slope)
            optimal_consumption = self.fuel_calculator.calculate_fuel_consumption_physical(optimal_speed, slope)
            
            current_consumptions.append(current_consumption)
            optimal_consumptions.append(optimal_consumption)
        
        # Анализ экономии - УБРАЛИ ЛИШНИЕ ПЕРЕМЕННЫЕ
        fuel_saving, saving_percentage = self.speed_optimizer.calculate_fuel_savings_analysis(
            current_speeds, optimal_speeds, slopes
        )
        
        # Создаем папку если её нет
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Расширенные колонки
            fieldnames = [
                'shirota', 'dolgota', 'elevation', 'slope_percent', 
                'current_speed', 'current_fuel_consumption',
                'smart_optimal_speed', 'smart_optimal_fuel_consumption',
                'fuel_saving', 'energy_saving'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            
            for i, point in enumerate(points):
                fuel_saving_point = current_consumptions[i] - optimal_consumptions[i]
                
                writer.writerow({
                    'shirota': f"{point['lat']:.6f}",
                    'dolgota': f"{point['lon']:.6f}",
                    'elevation': f"{elevations[i]:.1f}",
                    'slope_percent': f"{slopes[i]:.2f}",
                    'current_speed': f"{current_speeds[i]}",
                    'current_fuel_consumption': f"{current_consumptions[i]:.1f}",
                    'smart_optimal_speed': f"{optimal_speeds[i]}",
                    'smart_optimal_fuel_consumption': f"{optimal_consumptions[i]:.1f}",
                    'fuel_saving': f"{fuel_saving_point:.1f}",
                    'energy_saving': f"{energy_savings[i]:.1f}"
                })
        
        print(f"✅ Умный CSV файл создан: {filename}")
        
        # Детальная статистика - ИСПРАВЛЕННЫЙ ВЫЗОВ
        self._print_smart_statistics(current_speeds, optimal_speeds, current_consumptions, 
                                optimal_consumptions, slopes, route_length_km)  # УБРАЛИ 2 ЛИШНИХ АРГУМЕНТА
        
        return optimal_speeds, optimal_consumptions
    
    def _print_smart_statistics(self, current_speeds, optimal_speeds, current_consumptions, 
                            optimal_consumptions, slopes, route_length_km):
        """Вывод статистики с ФАКТИЧЕСКОЙ экономией"""
        avg_current_speed = sum(current_speeds) / len(current_speeds)
        avg_optimal_speed = sum(optimal_speeds) / len(optimal_speeds)
        
        # Расчет ФАКТИЧЕСКОЙ экономии для всего маршрута
        segment_length_km = route_length_km / len(current_consumptions)
        total_current_fuel = sum([(consumption * segment_length_km) / 100 
                                for consumption in current_consumptions])
        total_optimal_fuel = sum([(consumption * segment_length_km) / 100 
                                for consumption in optimal_consumptions])
        total_fuel_saved = total_current_fuel - total_optimal_fuel
        overall_saving_percent = (total_fuel_saved / total_current_fuel) * 100 if total_current_fuel > 0 else 0
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   🚗 Ваша средняя скорость: {avg_current_speed:.1f} км/ч")
        print(f"   🎯 Рекомендуемая скорость: {avg_optimal_speed:.1f} км/ч")
        print(f"   ⛽ Ваш средний расход: {sum(current_consumptions)/len(current_consumptions):.1f} л/100км")
        print(f"   💰 Рекомендуемый расход: {sum(optimal_consumptions)/len(optimal_consumptions):.1f} л/100км")
        print(f"   🔥 ФАКТИЧЕСКАЯ ЭКОНОМИЯ: {overall_saving_percent:.1f}%")
        print(f"   ⛽ Сэкономлено топлива: {total_fuel_saved:.2f} л")
        
        # Расчет денежной экономии (примерная цена 50 руб/литр)
        fuel_price = 50  # руб/литр
        money_saved = total_fuel_saved * fuel_price
        print(f"   💵 Сэкономлено денег: {money_saved:.0f} руб")
        
        # Анализ по типам участков
        flat_segments = [i for i, slope in enumerate(slopes) if abs(slope) < 2]
        uphill_segments = [i for i, slope in enumerate(slopes) if slope >= 2]
        downhill_segments = [i for i, slope in enumerate(slopes) if slope <= -2]
        
        if uphill_segments:
            uphill_current = sum(current_consumptions[i] for i in uphill_segments) / len(uphill_segments)
            uphill_optimal = sum(optimal_consumptions[i] for i in uphill_segments) / len(uphill_segments)
            uphill_saving = ((uphill_current - uphill_optimal) / uphill_current) * 100
            print(f"   📈 Экономия на подъемах: {uphill_saving:.1f}%")
        
        if downhill_segments:
            downhill_current = sum(current_consumptions[i] for i in downhill_segments) / len(downhill_segments)
            downhill_optimal = sum(optimal_consumptions[i] for i in downhill_segments) / len(downhill_segments)
            downhill_saving = ((downhill_current - downhill_optimal) / downhill_current) * 100
            print(f"   📉 Экономия на спусках: {downhill_saving:.1f}%")
        
        if flat_segments:
            flat_current = sum(current_consumptions[i] for i in flat_segments) / len(flat_segments)
            flat_optimal = sum(optimal_consumptions[i] for i in flat_segments) / len(flat_segments)
            flat_saving = ((flat_current - flat_optimal) / flat_current) * 100
            print(f"   🛣️  Экономия на ровной дороге: {flat_saving:.1f}%")
        
        # Рекомендации
        print(f"\n💡 ИТОГОВЫЕ РЕКОМЕНДАЦИИ:")
        if overall_saving_percent > 15:
            print("   🏆 Потрясающе! Вы могли бы сэкономить значительную сумму.")
        elif overall_saving_percent > 8:
            print("   👍 Отличный результат! Экономия ощутима.")
        elif overall_saving_percent > 3:
            print("   💰 Хорошо! Небольшая, но приятная экономия.")
        else:
            print("   📊 Ваше вождение уже достаточно экономично.")