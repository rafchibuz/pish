import requests
import polyline

class RouteFetcher:
    def __init__(self):
        self.osrm_url = "http://router.project-osrm.org/route/v1/driving"
    
    def get_route_data(self, start_point, end_point):
        """Получение данных маршрута из OSRM"""
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
        
