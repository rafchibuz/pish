import numpy as np
from src.route.fuel_calculator import FuelCalculator

class SmartSpeedOptimizer:
    def __init__(self, vehicle_mass=1500):
        self.fuel_calculator = FuelCalculator(vehicle_mass=vehicle_mass)
        self.vehicle_mass = vehicle_mass
        self.gravity = 9.81
        
    def calculate_energy_optimal_speed(self, slope_percent, current_speed, route_progress=0.5):
        """
        Расчет энергетически оптимальной скорости с учетом уклона
        
        Args:
            slope_percent: уклон в %
            current_speed: текущая скорость водителя (км/ч)
            route_progress: прогресс по маршруту (0-1)
        """
        slope_rad = np.arctan(slope_percent / 100)
        
        # Базовые параметры
        base_optimal = 65  # Базовая оптимальная скорость на ровной дороге
        
        if slope_percent > 1:  # ПОДЪЕМ
            # На подъеме снижаем скорость чтобы уменьшить работу против гравитации
            slope_impact = slope_percent * 1.5  # Коэффициент влияния уклона
            optimal_speed = base_optimal - min(15, slope_impact)
            
            # Учитываем прогресс маршрута - в начале можно экономить больше
            if route_progress < 0.3:  # В начале маршрута
                optimal_speed -= 2
            elif route_progress > 0.7:  # В конце маршрута
                optimal_speed += 2  # Можно немного ускориться
            
        elif slope_percent < -1:  # СПУСК
            # На спуске можно использовать гравитацию
            slope_impact = abs(slope_percent) * 1.2
            optimal_speed = base_optimal + min(10, slope_impact)
            
            # На спусках в начале маршрута разгоняемся меньше
            if route_progress < 0.2:
                optimal_speed -= 3
                
        else:  # РОВНАЯ ДОРОГА
            optimal_speed = base_optimal
        
        # Корректировка на основе текущей скорости водителя
        # Если водитель едет значительно быстрее оптимального - предлагаем сбросить
        speed_difference = current_speed - optimal_speed
        
        if speed_difference > 10:  # Если водитель едет слишком быстро
            optimal_speed += 3  # Небольшая коррекция в сторону водителя
        elif speed_difference < -15:  # Если водитель едет слишком медленно
            optimal_speed -= 2
        
        # Ограничения скорости
        optimal_speed = max(40, min(90, optimal_speed))
        
        return round(optimal_speed, 1)
    
    def calculate_smart_speed_profile(self, slopes, current_speeds, route_length):
        """
        Расчет умного профиля скоростей, который сглаживает расход
        
        Args:
            slopes: список уклонов для каждой точки
            current_speeds: текущие скорости водителя
            route_length: длина маршрута в км
        """
        print("🧠 Расчет умного профиля скоростей...")
        
        optimal_speeds = []
        energy_savings = []
        
        for i, (slope, current_speed) in enumerate(zip(slopes, current_speeds)):
            route_progress = i / len(slopes)
            
            # Расчет оптимальной скорости
            optimal_speed = self.calculate_energy_optimal_speed(
                slope, current_speed, route_progress
            )
            
            # Расчет экономии энергии
            current_energy = self._calculate_energy_consumption(current_speed, slope)
            optimal_energy = self._calculate_energy_consumption(optimal_speed, slope)
            energy_saving = current_energy - optimal_energy
            
            optimal_speeds.append(optimal_speed)
            energy_savings.append(energy_saving)
        
        # Пост-обработка: сглаживание резких скачков скорости
        optimal_speeds = self._smooth_speed_profile(optimal_speeds)
        
        # Расчет общей экономии
        total_energy_saving = sum(energy_savings)
        avg_energy_saving = total_energy_saving / len(energy_savings)
        
        print(f"💡 Средняя экономия энергии: {avg_energy_saving:.1f} Дж/м")
        print(f"💰 Общая экономия энергии: {total_energy_saving:.0f} Дж")
        
        return optimal_speeds, energy_savings
    
    def _calculate_energy_consumption(self, speed_kmh, slope_percent):
        """Расчет потребления энергии на метр пути (Дж/м)"""
        speed_ms = speed_kmh / 3.6
        slope_rad = np.arctan(slope_percent / 100)
        
        # Сила сопротивления качению
        rolling_force = 0.015 * self.vehicle_mass * self.gravity
        
        # Сила аэродинамического сопротивления
        air_force = 0.5 * 1.2 * 0.3 * 2.2 * speed_ms**2
        
        # Сила сопротивления подъему
        grade_force = self.vehicle_mass * self.gravity * np.sin(slope_rad)
        
        # Общая сила
        total_force = rolling_force + air_force + grade_force
        
        # Энергия на метр пути (Дж/м)
        energy_per_meter = total_force
        
        return energy_per_meter
    
    def _smooth_speed_profile(self, speeds, max_change=5):
        """Сглаживание профиля скоростей чтобы избежать резких изменений"""
        smoothed = [speeds[0]]  # Начальная скорость
        
        for i in range(1, len(speeds)):
            prev_speed = smoothed[-1]
            current_speed = speeds[i]
            
            # Ограничиваем максимальное изменение скорости
            if abs(current_speed - prev_speed) > max_change:
                if current_speed > prev_speed:
                    smoothed_speed = prev_speed + max_change
                else:
                    smoothed_speed = prev_speed - max_change
            else:
                smoothed_speed = current_speed
            
            smoothed.append(smoothed_speed)
        
        return smoothed
    
    def calculate_fuel_savings_analysis(self, current_speeds, optimal_speeds, slopes):
        """Анализ экономии топлива"""
        print("⛽ Анализ экономии топлива...")
        
        current_total_fuel = 0
        optimal_total_fuel = 0
        
        for i, (current_speed, optimal_speed, slope) in enumerate(zip(current_speeds, optimal_speeds, slopes)):
            current_fuel = self.fuel_calculator.calculate_fuel_consumption_physical(current_speed, slope)
            optimal_fuel = self.fuel_calculator.calculate_fuel_consumption_physical(optimal_speed, slope)
            
            current_total_fuel += current_fuel
            optimal_total_fuel += optimal_fuel
        
        avg_current_fuel = current_total_fuel / len(current_speeds)
        avg_optimal_fuel = optimal_total_fuel / len(optimal_speeds)
        fuel_saving_per_100km = avg_current_fuel - avg_optimal_fuel
        saving_percentage = (fuel_saving_per_100km / avg_current_fuel) * 100
        
        print(f"📊 АНАЛИЗ ЭКОНОМИИ:")
        print(f"   🚗 Текущий средний расход: {avg_current_fuel:.1f} л/100км")
        print(f"   🎯 Оптимальный средний расход: {avg_optimal_fuel:.1f} л/100км")
        print(f"   💰 Экономия: {fuel_saving_per_100km:.1f} л/100км")
        print(f"   📈 Экономия: {saving_percentage:.1f}%")
        
        return fuel_saving_per_100km, saving_percentage