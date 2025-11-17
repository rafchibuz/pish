import requests
import numpy as np

class ElevationCalculator:
    def __init__(self):
        self.open_elevation_url = "https://api.open-elevation.com/api/v1/lookup"
    
    def get_elevation_data(self, points):
        """Получение данных о высотах для точек маршрута"""
        print("🏔️  Получение данных о высотах...")
        
        # Формируем запрос к API высот
        locations = [{"latitude": point['lat'], "longitude": point['lon']} for point in points]
        
        try:
            response = requests.post(
                self.open_elevation_url,
                json={"locations": locations},
                timeout=30
            )
            data = response.json()
            
            elevations = [result['elevation'] for result in data['results']]
            
            # Рассчитываем уклоны между точками
            slopes = self.calculate_slopes(points, elevations)
            
            print(f"✅ Получены данные о высотах для {len(elevations)} точек")
            print(f"📊 Диапазон высот: {min(elevations):.1f} - {max(elevations):.1f} м")
            
            return elevations, slopes
            
        except Exception as e:
            print(f"❌ Ошибка получения данных о высотах: {e}")
            # Возвращаем нулевые высоты и уклоны
            return [0] * len(points), [0] * len(points)
    
    def calculate_slopes(self, points, elevations):
        """Расчет уклонов между точками (в %)"""
        slopes = [0]  # Первая точка без уклона
        
        for i in range(1, len(points)):
            # Расчет расстояния между точками
            distance = self._calculate_distance(
                points[i-1]['lat'], points[i-1]['lon'],
                points[i]['lat'], points[i]['lon']
            )
            
            if distance > 0:
                height_diff = elevations[i] - elevations[i-1]
                slope = (height_diff / distance) * 100  # Уклон в %
            else:
                slope = 0
            
            slopes.append(slope)
        
        return slopes
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Расчет расстояния между двумя точками в метрах"""
        R = 6371000  # Радиус Земли в метрах
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c