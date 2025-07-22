(function waitForDjangoJQuery(cb) {
    if (typeof django !== 'undefined' && typeof django.jQuery === 'function') {
        cb(django.jQuery);
    } else {
        setTimeout(waitForDjangoJQuery, 50, cb);
    }
})(function($) {
    $(function () {
        const $categoryCheckboxes = $('input[name="categories"]');
        const $services = $('#id_services');

        // Вынеси debounce наружу, чтобы он был ОДИН для всех чекбоксов
        function onCategoriesChange() {
            const checkedIds = $categoryCheckboxes
                .filter(':checked')
                .map(function() { return this.value; })
                .get();

            if (checkedIds.length === 0) {
                $services.empty();
                $services.trigger('change');
                return;
            }
            $.get('/admin/get_services_by_category/', {category_ids: checkedIds.join(',')}, function (data) {
                $services.empty();
                if (data.services && data.services.length > 0) {
                    data.services.forEach(function(service) {
                        $services.append(new Option(service.name, service.id, false, false));
                    });
                    const ids = data.services.map(service => String(service.id));
                    $services.val(ids).trigger('change');
                } else {
                    $services.val([]).trigger('change');
                }
            });
        }

        // Создаем один debounce для всей группы чекбоксов
        const debouncedChange = debounce(onCategoriesChange, 300);

        $categoryCheckboxes.off('change.get_services_by_category').on('change.get_services_by_category', debouncedChange);

        // debounce объяви тоже выше!
        function debounce(fn, delay) {
            let timer = null;
            return function() {
                clearTimeout(timer);
                timer = setTimeout(() => fn.apply(this, arguments), delay);
            };
        }
    });
});
