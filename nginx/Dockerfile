FROM nginx:1.26.0

COPY ./html /var/www/html

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY ./nginx_entrypoint.sh /docker-entrypoint.d/.
COPY ./autorenew_hook.sh /etc/letsencrypt/renewal-hooks/deploy/.

RUN chmod +x /docker-entrypoint.d/nginx_entrypoint.sh
RUN apt update
RUN apt install certbot python3-certbot-nginx -y
