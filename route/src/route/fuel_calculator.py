import numpy as np

class FuelCalculator:
    def __init__(self, vehicle_mass=1500, engine_efficiency=0.3, fuel_density=0.74):
        self.vehicle_mass = vehicle_mass  # кг
        self.engine_efficiency = engine_efficiency  # КПД двигателя
        self.fuel_density = fuel_density  # кг/л (плотность бензина)
        self.air_density = 1.2  # кг/м³
        self.drag_coefficient = 0.3
        self.frontal_area = 2.2  # м²
        self.rolling_resistance = 0.015
        self.gravity = 9.81  # м/с²
        
    def calculate_power_requirements(self, speed_kmh, slope_percent):
        """Расчет требуемой мощности с учетом физики движения"""
        speed_ms = speed_kmh / 3.6  # м/с
        
        # 1. Сопротивление качению
        rolling_force = self.rolling_resistance * self.vehicle_mass * self.gravity
        
        # 2. Аэродинамическое сопротивление
        air_force = 0.5 * self.air_density * self.drag_coefficient * self.frontal_area * speed_ms**2
        
        # 3. Сопротивление подъему (уклон в радианы)
        slope_rad = np.arctan(slope_percent / 100)
        grade_force = self.vehicle_mass * self.gravity * np.sin(slope_rad)
        
        # 4. Общая сила сопротивления
        total_force = rolling_force + air_force + grade_force
        
        # 5. Требуемая мощность (Вт)
        power_watts = total_force * speed_ms
        
        return power_watts
    
    def calculate_fuel_consumption_physical(self, speed_kmh, slope_percent, distance_km=1):
        """Расчет расхода топлива на основе физической модели (л/100км)"""
        # Требуемая мощность
        power_watts = self.calculate_power_requirements(speed_kmh, slope_percent)
        power_kw = power_watts / 1000
        
        # Время поездки (часы)
        time_hours = distance_km / speed_kmh if speed_kmh > 0 else 0
        
        # Энергия за поездку (кВт*ч)
        energy_kwh = power_kw * time_hours
        
        # Теплотворная способность бензина (кВт*ч/кг)
        fuel_energy_density = 11.8  # кВт*ч/кг
        
        # Масса топлива (кг)
        fuel_mass_kg = energy_kwh / (fuel_energy_density * self.engine_efficiency)
        
        # Объем топлива (литры)
        fuel_liters = fuel_mass_kg / self.fuel_density
        
        # Расход в л/100км
        fuel_consumption_per_100km = (fuel_liters / distance_km) * 100 if distance_km > 0 else 0
        
        return max(3.0, fuel_consumption_per_100km)
    
    def find_optimal_speed_for_slope(self, slope_percent, speed_range=range(30, 121, 5)):
        """Поиск оптимальной скорости для конкретного уклона"""
        best_speed = 60
        best_consumption = float('inf')
        
        for speed in speed_range:
            consumption = self.calculate_fuel_consumption_physical(speed, slope_percent)
            
            if consumption < best_consumption:
                best_consumption = consumption
                best_speed = speed
        
        return best_speed, best_consumption
    
    def calculate_route_optimal_speeds(self, slopes, segment_distances):
        """Расчет оптимальных скоростей для всего маршрута"""
        optimal_speeds = []
        optimal_consumptions = []
        
        for i, slope in enumerate(slopes):
            optimal_speed, optimal_consumption = self.find_optimal_speed_for_slope(slope)
            optimal_speeds.append(optimal_speed)
            optimal_consumptions.append(optimal_consumption)
        
        return optimal_speeds, optimal_consumptions