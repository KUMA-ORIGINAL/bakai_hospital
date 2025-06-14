#!/bin/sh

get_certs_lower=$(echo "$GET_CERTS" | tr '[:upper:]' '[:lower:]')

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
            -d "$domain" -d "www.$domain"
    done

    echo "🔄 Перезапуск nginx..."
    nginx -s reload
    sleep 2
fi
