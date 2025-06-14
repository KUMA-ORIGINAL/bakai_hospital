#!/bin/sh

set -e  # Останавливаем скрипт при любой ошибке

# Приводим GET_CERTS к нижнему регистру
get_certs_lower=$(echo "$GET_CERTS" | tr '[:upper:]' '[:lower:]')

# Проверяем наличие обязательных переменных
if [ -z "$DOMAIN" ] || [ -z "$CORE_DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
    echo "❌ Ошибка: Не заданы обязательные переменные DOMAIN, CORE_DOMAIN или CERTBOT_EMAIL"
    exit 1
fi

if [ "$get_certs_lower" = "true" ]; then
    echo "🔧 Начинаем процесс получения SSL сертификатов..."

    # Проверяем, что nginx запущен
    if ! nginx -t > /dev/null 2>&1; then
        echo "❌ Ошибка: Конфигурация nginx некорректна"
        exit 1
    fi

    domains="$DOMAIN $CORE_DOMAIN"
    cert_obtained=false

    for domain in $domains; do
        echo "🆕 Получаем или обновляем сертификат для $domain..."

        # Проверяем доступность домена (опционально)
        if ! nslookup "$domain" > /dev/null 2>&1; then
            echo "⚠️  Предупреждение: Домен $domain может быть недоступен"
        fi

        # Получаем сертификат с обработкой ошибок
        if certbot certonly \
            --nginx \
            --email "$CERTBOT_EMAIL" \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            --expand \
            --keep-until-expiring \
            -d "$domain" -d "www.$domain"; then

            echo "✅ Сертификат для $domain успешно получен/обновлен"
            cert_obtained=true
        else
            echo "❌ Ошибка получения сертификата для $domain"
            # Продолжаем выполнение для других доменов
        fi
    done

    # Перезапускаем nginx только если хотя бы один сертификат был получен
    if [ "$cert_obtained" = true ]; then
        echo "🔄 Перезапуск nginx..."

        # Сначала проверяем конфигурацию
        if nginx -t; then
            # Graceful reload вместо полной остановки
            nginx -s reload
            echo "✅ Nginx успешно перезапущен"
        else
            echo "❌ Ошибка в конфигурации nginx, перезапуск отменен"
            exit 1
        fi
    else
        echo "⚠️  Сертификаты не были получены, nginx не перезапускается"
    fi

    echo "🎉 Процесс завершен!"
else
    echo "ℹ️  GET_CERTS не равен 'true', пропускаем получение сертификатов"
fi