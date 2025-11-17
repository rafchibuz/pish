import requests
import csv
import folium
import polyline
import random
import numpy as np
from folium import plugins

class RouteMapper:
    def __init__(self):
        self.osrm_url = "http://router.project-osrm.org/route/v1/driving"
        
    def get_route_data(self, start_point, end_point):
        """Получение данных маршрута"""
        print("🛣️  Получение маршрута...")
        
        # Поддерживаем разные форматы ввода координат
        if isinstance(start_point, str):
            start_lat, start_lon = start_point.split(',')
        else:
            start_lat, start_lon = start_point
            
        if isinstance(end_point, str):
            end_lat, end_lon = end_point.split(',')
        else:
            end_lat, end_lon = end_point
        
        # Преобразуем в float
        start_lat, start_lon = float(start_lat), float(start_lon)
        end_lat, end_lon = float(end_lat), float(end_lon)
        
        url = f"{self.osrm_url}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'overview': 'full',
            'geometries': 'polyline',
            'steps': 'false'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data['code'] == 'Ok':
                route = data['routes'][0]
                geometry = polyline.decode(route['geometry'])
                points = [{'lat': lat, 'lon': lon} for lat, lon in geometry]
                
                print(f"✅ Получено {len(points)} точек маршрута")
                print(f"📏 Расстояние: {route['distance']/1000:.1f} км")
                print(f"⏱️  Время в пути: {route['duration']/60:.1f} мин")
                print(f"📍 Начало: {start_lat:.4f}, {start_lon:.4f}")
                print(f"📍 Конец: {end_lat:.4f}, {end_lon:.4f}")
                
                return points, route
            else:
                print("❌ Ошибка получения маршрута")
                return None, None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None, None
    
    def generate_realistic_speeds(self, num_points, route_length_km):
        """Генерация реалистичных скоростей для маршрута"""
        print("🚗 Генерация реалистичных скоростей...")
        
        speeds = []
        current_speed = random.randint(40, 60)  # Начальная скорость
        
        for i in range(num_points):
            progress = i / num_points
            
            # Базовое изменение скорости с учетом прогресса маршрута
            base_speed = 50 + 15 * np.sin(progress * 6 * np.pi)
            
            # Случайные колебания
            speed_change = random.randint(-5, 5)
            current_speed += speed_change
            
            # Ограничения скорости
            if current_speed < 20:  # Минимальная скорость в городе
                current_speed = 20
            elif current_speed > 90:  # Максимальная скорость
                current_speed = 90 - random.randint(0, 10)
            
            # Имитация светофоров и остановок
            if i % random.randint(15, 25) == 0 and i > 0:
                current_speed = max(0, current_speed - random.randint(20, 40))
            
            # Имитация разгонов после остановок
            if i > 0 and speeds[-1] < 10:
                current_speed = random.randint(30, 50)
            
            speeds.append(round(current_speed, 1))
        
        return speeds
    
    def create_csv_file(self, points, route_length_km, filename='маршрут_с_скоростями.csv'):
        """Создание CSV файла с координатами и скоростями"""
        print("💾 Создание CSV файла с координатами и скоростями...")
        
        # Генерируем реалистичные скорости
        speeds = self.generate_realistic_speeds(len(points), route_length_km)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Координаты + скорость
            fieldnames = ['shirota', 'dolgota', 'speed_kmh']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            
            for i, point in enumerate(points):
                writer.writerow({
                    'shirota': f"{point['lat']:.6f}",
                    'dolgota': f"{point['lon']:.6f}",
                    'speed_kmh': f"{speeds[i]}"
                })
        
        print(f"✅ CSV файл создан: {filename}")
        
        # Выводим пример данных
        print("\n📋 Пример данных из CSV:")
        print("shirota, dolgota, speed_kmh")
        if points:
            print(f"{points[0]['lat']:.6f}, {points[0]['lon']:.6f}, {speeds[0]}")
            if len(points) > 1:
                print(f"{points[1]['lat']:.6f}, {points[1]['lon']:.6f}, {speeds[1]}")
            if len(points) > 2:
                print(f"{points[-1]['lat']:.6f}, {points[-1]['lon']:.6f}, {speeds[-1]}")
        
        # Статистика по скоростям
        avg_speed = sum(speeds) / len(speeds)
        print(f"\n📊 Статистика скоростей:")
        print(f"   📏 Средняя скорость: {avg_speed:.1f} км/ч")
        print(f"   🚀 Максимальная скорость: {max(speeds)} км/ч")
        print(f"   🐌 Минимальная скорость: {min(speeds)} км/ч")
    
    def create_static_map(self, points, route_info, filename='маршрут_карта.html'):
        """Создание статической карты с маршрутом"""
        print("🗺️  Создание карты...")
        
        if not points:
            print("❌ Нет точек для создания карты")
            return None
        
        # Центр карты - середина маршрута
        center_lat = sum(p['lat'] for p in points) / len(points)
        center_lon = sum(p['lon'] for p in points) / len(points)
        
        # Создаем карту
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Добавляем маршрут
        route_coords = [[p['lat'], p['lon']] for p in points]
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=5,
            opacity=0.7,
            popup=f"Маршрут: {route_info['distance']/1000:.1f} км"
        ).add_to(m)
        
        # Добавляем начальную и конечную точки
        folium.Marker(
            [points[0]['lat'], points[0]['lon']],
            popup=f'🏁 СТАРТ<br>Широта: {points[0]["lat"]:.4f}<br>Долгота: {points[0]["lon"]:.4f}',
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        folium.Marker(
            [points[-1]['lat'], points[-1]['lon']],
            popup=f'🏁 ФИНИШ<br>Широта: {points[-1]["lat"]:.4f}<br>Долгота: {points[-1]["lon"]:.4f}',
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # Добавляем мини-карту
        plugins.MiniMap().add_to(m)
        
        # Добавляем измерение расстояния
        plugins.MeasureControl().add_to(m)
        
        # Добавляем информацию о маршруте
        route_info_html = f"""
        <div style="
            position: fixed; 
            bottom: 20px; 
            left: 20px; 
            background: white; 
            padding: 10px; 
            border-radius: 5px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-family: Arial; 
            font-size: 12px;
            z-index: 1000;
        ">
            <b>📊 ИНФОРМАЦИЯ О МАРШРУТЕ</b><br>
            📏 Расстояние: {route_info['distance']/1000:.1f} км<br>
            ⏱️ Время: {route_info['duration']/60:.1f} мин<br>
            📍 Точек: {len(points)}<br>
            🏁 Начало: {points[0]['lat']:.4f}, {points[0]['lon']:.4f}<br>
            🏁 Конец: {points[-1]['lat']:.4f}, {points[-1]['lon']:.4f}
        </div>
        """
        m.get_root().html.add_child(folium.Element(route_info_html))
        
        # Сохраняем карту
        m.save(filename)
        print(f"✅ Карта сохранена как '{filename}'")
        
        return m
    
    def generate_route(self, start_point, end_point, map_filename='маршрут_карта.html', csv_filename='маршрут_с_скоростями.csv'):
        """Основная функция генерации маршрута"""
        print("🚀 ГЕНЕРАЦИЯ МАРШРУТА")
        print("=" * 50)
        
        # Получаем данные маршрута
        points, route_info = self.get_route_data(start_point, end_point)
        if not points:
            print("❌ Не удалось получить маршрут")
            return False
        
        # Создаем CSV файл с координатами и скоростями
        route_length_km = route_info['distance'] / 1000
        self.create_csv_file(points, route_length_km, csv_filename)
        
        # Создаем карту
        self.create_static_map(points, route_info, map_filename)
        
        # Выводим статистику
        print(f"\n📊 СТАТИСТИКА МАРШРУТА:")
        print(f"   📏 Общее расстояние: {route_length_km:.1f} км")
        print(f"   ⏱️  Время в пути: {route_info['duration']/60:.1f} мин")
        print(f"   📍 Количество точек: {len(points)}")
        
        print(f"\n🎉 Готово!")
        print(f"   📄 Координаты + скорости: {csv_filename}")
        print(f"   🗺️  Карта: {map_filename}")
        
        return True

# Примеры маршрутов для тестирования
ROUTE_EXAMPLES = {
    "1": {
        "name": "Москва: Красная площадь → МГУ",
        "start": "55.7539,37.6208",
        "end": "55.7033,37.5307"
    },
    "2": {
        "name": "Москва: ВДНХ → Парк Горького", 
        "start": "55.8219,37.6311",
        "end": "55.7317,37.6033"
    },
    "3": {
        "name": "Санкт-Петербург: Эрмитаж → Петропавловская крепость",
        "start": "59.9398,30.3146", 
        "end": "59.9500,30.3167"
    },
    "4": {
        "name": "Москва - Питер",
        "start": "55.703946,37.644581", 
        "end": "59.938369,30.312683"
    }
}

# Главная функция
def main():
    mapper = RouteMapper()
    
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
        map_filename = f'маршрут_{choice}.html'
        csv_filename = f'маршрут_{choice}_скорости.csv'
    elif choice.lower() == 'custom':
        print("\n📍 ВВЕДИТЕ КООРДИНАТЫ:")
        start_point = input("Начальная точка (широта,долгота): ").strip()
        end_point = input("Конечная точка (широта,долгота): ").strip()
        map_filename = 'маршрут_пользовательский.html'
        csv_filename = 'маршрут_пользовательский_скорости.csv'
    else:
        # По умолчанию используем первый маршрут
        route = ROUTE_EXAMPLES["1"]
        start_point = route["start"]
        end_point = route["end"]
        map_filename = 'маршрут_по_умолчанию.html'
        csv_filename = 'маршрут_по_умолчанию_скорости.csv'
    
    print(f"\n📍 МАРШРУТ: {start_point} → {end_point}")
    
    success = mapper.generate_route(
        start_point=start_point,
        end_point=end_point,
        map_filename=map_filename,
        csv_filename=csv_filename
    )
    
    if success:
        print(f"\n✨ Файлы успешно созданы!")
        print(f"   📄 CSV с координатами и скоростями: {csv_filename}")
        print(f"   🗺️  Карта: {map_filename}")
        print(f"\n📋 В CSV файле 3 колонки:")
        print("   - shirota (широта в градусах)")
        print("   - dolgota (долгота в градусах)")
        print("   - speed_kmh (скорость в км/ч)")
    else:
        print("\n💥 Ошибка создания маршрута")

if __name__ == "__main__":
    main()