def parse_coordinates(point):
    """Парсинг координат из разных форматов"""
    if isinstance(point, str):
        lat, lon = point.split(',')
        return float(lat), float(lon)
    return point

def calculate_distance(point1, point2):
    """Расчет расстояния между точками"""
    lat1, lon1 = point1
    lat2, lon2 = point2
        
    # Упрощенный расчет расстояния
    R = 6371000  # Радиус Земли в метрах
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
        
    return distance