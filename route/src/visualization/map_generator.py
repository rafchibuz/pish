import folium
from folium import plugins

class MapGenerator:
    def create_static_map(self, points, route_info, filename):
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