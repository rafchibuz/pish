import random
import numpy as np

class DataProcessor:
    def __init__(self):
        pass
    
    def generate_realistic_speeds(self, num_points, route_length_km):
        """Генерация реалистичных скоростей для маршрута (текущая скорость)"""
        print("🚗 Генерация реалистичных скоростей...")
        
        speeds = []
        current_speed = random.randint(40, 60)
        
        for i in range(num_points):
            progress = i / num_points
            
            # Базовое изменение скорости с учетом прогресса маршрута
            base_speed = 50 + 15 * np.sin(progress * 6 * np.pi)
            
            # Случайные колебания
            speed_change = random.randint(-5, 5)
            current_speed += speed_change
            
            # Ограничения скорости
            if current_speed < 20:
                current_speed = 20
            elif current_speed > 90:
                current_speed = 90 - random.randint(0, 10)
            
            # Имитация светофоров и остановок
            if i % random.randint(15, 25) == 0 and i > 0:
                current_speed = max(0, current_speed - random.randint(20, 40))
            
            # Имитация разгонов после остановок
            if i > 0 and speeds and speeds[-1] < 10:
                current_speed = random.randint(30, 50)
            
            speeds.append(round(current_speed, 1))
        
        return speeds