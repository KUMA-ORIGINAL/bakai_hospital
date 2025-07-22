import json

from services.models import Category, Service

with open('services/fixtures/services_by_category.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

for category_name, services in categories.items():
    # Создаём категорию, если нет
    category, created = Category.objects.get_or_create(name=category_name, organization_id=1)

    for service in services:
        try:
            # Пробуем найти услугу по имени (можно добавить другие фильтры, если нужно)
            service_obj = Service.objects.get(name=service['Наименование'])
            # Привязываем к категории, если ещё не привязан или категория не совпадает
            if service_obj.category != category:
                service_obj.category = category
                service_obj.save()
                print(f'Услуга "{service_obj.name}" привязана к категории "{category.name}"')
            else:
                print(f'Услуга "{service_obj.name}" уже привязана к категории "{category.name}"')
        except Service.DoesNotExist:
            # Не создаём услугу!
            print(f'Услуга "{service["Наименование"]}" не найдена, не создаём.')

