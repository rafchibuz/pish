from src.route.route_fetcher import RouteFetcher
from src.route.data_processor import DataProcessor
from src.route.csv_generator import CSVGenerator
from src.visualization.map_generator import MapGenerator
from src.visualization.animation import CarAnimation
from src.utils.config import ROUTE_EXAMPLES

class RouteManager:
    """Основной класс для управления всем процессом"""
    def __init__(self):
        self.route_fetcher = RouteFetcher()
        self.data_processor = DataProcessor()
        self.csv_generator = CSVGenerator()  # ← Здесь уже используется ElevationCalculator
        self.map_generator = MapGenerator()
    
    def generate_route(self, start_point, end_point, map_filename, csv_filename):
        """Полный процесс генерации маршрута"""
        print("🚀 ГЕНЕРАЦИЯ МАРШРУТА С ОПТИМИЗАЦИЕЙ")
        print("=" * 50)
        
        # Получаем данные маршрута
        points, route_info = self.route_fetcher.get_route_data(start_point, end_point)
        if not points:
            return False
        
        # Создаем CSV с умной оптимизацией
        route_length_km = route_info['distance'] / 1000
        self.csv_generator.create_csv_file(points, route_length_km, csv_filename)
        
        # Создаем карту
        self.map_generator.create_static_map(points, route_info, map_filename)
        
        # Упрощенная статистика
        print(f"\n📊 ИТОГИ МАРШРУТА:")
        print(f"   📏 Расстояние: {route_length_km:.1f} км")
        print(f"   ⏱️  Время: {route_info['duration']/60:.1f} мин")
        print(f"   📍 Точек: {len(points)}")
        
        return True

def main():
    """Главная функция"""
    print("🚀 СИСТЕМА ВИЗУАЛИЗАЦИИ МАРШРУТОВ")
    print("=" * 50)
    
    # Создаем необходимые директории
    import os
    os.makedirs('output/maps', exist_ok=True)
    os.makedirs('output/csv', exist_ok=True)
    
    manager = RouteManager()
    
    # Выбор маршрута
    print("🎯 ВЫБЕРИТЕ МАРШРУТ:")
    for key, route in ROUTE_EXAMPLES.items():
        print(f"   {key}. {route['name']}")
    
    print("\n   ИЛИ введите свои координаты:")
    print("   Формат: широта,долгота (например: 55.7558,37.6173)")
    
    choice = input("\n🎲 Ваш выбор (1-4 или 'custom'): ").strip()
    
    if choice in ROUTE_EXAMPLES:
        route = ROUTE_EXAMPLES[choice]
        start_point = route["start"]
        end_point = route["end"]
        map_filename = f'output/maps/маршрут_{choice}.html'
        csv_filename = f'output/csv/маршрут_{choice}_скорости.csv'
    elif choice.lower() == 'custom':
        print("\n📍 ВВЕДИТЕ КООРДИНАТЫ:")
        start_point = input("Начальная точка (широта,долгота): ").strip()
        end_point = input("Конечная точка (широта,долгота): ").strip()
        map_filename = 'output/maps/маршрут_пользовательский.html'
        csv_filename = 'output/csv/маршрут_пользовательский_скорости.csv'
    else:
        route = ROUTE_EXAMPLES["1"]
        start_point = route["start"]
        end_point = route["end"]
        map_filename = 'output/maps/маршрут_по_умолчанию.html'
        csv_filename = 'output/csv/маршрут_по_умолчанию_скорости.csv'
        print(f"⚠️  Используется маршрут по умолчанию")
    
    print(f"\n📍 МАРШРУТ: {start_point} → {end_point}")
    
    # Генерация маршрута
    success = manager.generate_route(start_point, end_point, map_filename, csv_filename)
    
    if success:
        print(f"\n✅ Маршрут создан!")
        print(f"   📄 CSV с координатами и скоростями: {csv_filename}")
        print(f"   🗺️  Карта: {map_filename}")
        
        # Запуск анимации
        animate = input("\n🎬 Запустить анимацию? (y/n): ").lower().strip()
        if animate == 'y':
            try:
                print("\n🎬 ЗАПУСК АНИМАЦИИ...")
                animation = CarAnimation(csv_filename)
                animation.show()
            except Exception as e:
                print(f"❌ Ошибка анимации: {e}")

if __name__ == "__main__":
    main()