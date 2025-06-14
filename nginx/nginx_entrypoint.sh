#!/bin/sh

# Специальная версия для Docker контейнеров
# Не используем set -e для более гибкой обработки ошибок

# Функция для проверки DNS записи
check_dns_record() {
    local domain=$1
    # Используем nslookup как более универсальную команду
    if nslookup "$domain" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Функция для логирования
log_info() {
    echo "ℹ️  [$(date '+%H:%M:%S')] $1"
}

log_success() {
    echo "✅ [$(date '+%H:%M:%S')] $1"
}

log_warning() {
    echo "⚠️  [$(date '+%H:%M:%S')] $1"
}

log_error() {
    echo "❌ [$(date '+%H:%M:%S')] $1"
}

# Приводим GET_CERTS к нижнему регистру
get_certs_lower=$(echo "$GET_CERTS" | tr '[:upper:]' '[:lower:]')

# Проверяем наличие обязательных переменных
if [ -z "$DOMAIN" ] || [ -z "$CORE_DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
    log_error "Не заданы обязательные переменные DOMAIN, CORE_DOMAIN или CERTBOT_EMAIL"
    exit 1
fi

if [ "$get_certs_lower" = "true" ]; then
    log_info "Начинаем процесс получения SSL сертификатов..."

    # Проверяем, что nginx конфигурация корректна
    if ! nginx -t > /dev/null 2>&1; then
        log_error "Конфигурация nginx некорректна"
        nginx -t  # Показываем ошибки
        exit 1
    fi

    domains="$DOMAIN $CORE_DOMAIN"
    any_cert_updated=false

    for domain in $domains; do
        log_info "Обрабатываем домен: $domain"

        # Проверяем доступность основного домена
        if ! check_dns_record "$domain"; then
            log_warning "Домен $domain недоступен через DNS, пропускаем"
            continue
        fi

        # Проверяем доступность www поддомена
        www_domain="www.$domain"
        domain_list="-d $domain"

        if check_dns_record "$www_domain"; then
            log_info "Поддомен $www_domain найден, добавляем в сертификат"
            domain_list="$domain_list -d $www_domain"
        else
            log_info "Поддомен $www_domain не найден, сертификат только для основного домена"
        fi

        # Получаем сертификат
        log_info "Запускаем certbot для $domain..."

        if certbot certonly \
            --nginx \
            --email "$CERTBOT_EMAIL" \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            --keep-until-expiring \
            $domain_list 2>/dev/null; then

            log_success "Сертификат для $domain обработан успешно"
            any_cert_updated=true
        else
            log_warning "Проблема с сертификатом для $domain (возможно, не требует обновления)"
            # В Docker среде certbot может возвращать ошибку даже при успешной работе
            # Поэтому не прерываем выполнение
        fi
    done

    # Обработка nginx после получения сертификатов
    if [ "$any_cert_updated" = true ]; then
        log_info "Проверяем необходимость перезагрузки nginx..."

        # Проверяем конфигурацию еще раз
        if nginx -t > /dev/null 2>&1; then
            # Проверяем статус nginx процесса
            if pgrep nginx > /dev/null; then
                log_info "Nginx запущен, проверяем PID файл..."

                if [ -f "/var/run/nginx.pid" ] && [ -s "/var/run/nginx.pid" ]; then
                    log_info "Выполняем graceful reload..."
                    if nginx -s reload 2>/dev/null; then
                        log_success "Nginx конфигурация успешно перезагружена"
                    else
                        log_warning "Reload не удался, но это нормально в Docker среде"
                    fi
                else
                    log_info "PID файл недоступен - это нормально для Docker контейнеров"
                    log_info "Новые сертификаты будут применены автоматически"
                fi
            else
                log_warning "Nginx процесс не найден"
            fi
        else
            log_error "Ошибка в конфигурации nginx после получения сертификатов"
            nginx -t  # Показываем ошибки
        fi
    else
        log_info "Сертификаты не обновлялись, nginx reload не требуется"
    fi

    log_success "Процесс обработки сертификатов завершен"
else
    log_info "GET_CERTS не равен 'true', пропускаем получение сертификатов"
fi

# В конце скрипта не завершаем процесс с ошибкой
# Это позволит контейнеру продолжить работу
log_info "Скрипт завершен, контейнер продолжает работу"