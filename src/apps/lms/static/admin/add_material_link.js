(function($) {
  $(document).ready(() => {
    const id = $('.field-material_id .readonly').html();
    if (id == "None") {  // fuck
      return;
    }

    const title = $('.field-material_title .readonly').html();
    const link = `/admin/notion/material/${id}/change/`;

    $('.field-material input').after(`<p class="material_link">«${title}», <a href="${link}">редактировать→</a>`);

  });
})(django.jQuery);
