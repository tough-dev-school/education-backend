(function($) {
  $(document).ready(() => {
    const $select = $('.field-call #id_call');
    $select.css('display', 'none');

    const updateCallName = () => {
      const callName = $select.find(':selected').text();
      $('p.call-name').remove();
      $select.after(`<p class="call-name">${callName}</p>`);
    };

    $select.on('change', updateCallName);
    updateCallName();

  });
})(django.jQuery);
