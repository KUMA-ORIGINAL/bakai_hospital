#!/bin/sh

# Приводим GET_CERTS к нижнему регистру
get_certs_lower=$(echo "$GET_CERTS" | tr '[:upper:]' '[:lower:]')

# Если GET_CERTS=true
if [ "$get_certs_lower" = "true" ]; then

    domains="$DOMAIN $CORE_DOMAIN"

    for domain in $domains; do
        echo "🆕 Получаем или обновляем сертификат для $domain..."
        certbot --nginx \
            --email "$CERTBOT_EMAIL" \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            --expand \
            --reinstall \
            -d "$domain" -d "www.$domain"
    done

    # Перезапуск nginx после получения всех сертификатов
    echo "🔄 Перезапуск nginx..."
    nginx -s stop
    sleep 2
fi
