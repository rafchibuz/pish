import os
import glob

print("🔍 Поиск файлов нейросети...")

# Ищем все .pkl файлы
pkl_files = glob.glob("**/*.pkl", recursive=True)

if pkl_files:
    print("✅ Найдены файлы моделей:")
    for file in pkl_files:
        print(f"   📁 {file} → {os.path.abspath(file)}")
else:
    print("❌ Файлы .pkl не найдены!")
    
# Проверяем папку models
models_dir = 'models'
if os.path.exists(models_dir):
    print(f"\n📂 Содержимое папки {models_dir}:")
    for item in os.listdir(models_dir):
        print(f"   📄 {item}")
else:
    print(f"\n❌ Папка {models_dir} не существует!")

# Проверяем текущую директорию
print(f"\n📍 Текущая рабочая директория: {os.getcwd()}")