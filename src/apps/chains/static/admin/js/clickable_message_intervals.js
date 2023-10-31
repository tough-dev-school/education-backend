(function ($) {
  $(document).ready(() => {
    const delayField = "#message_form input#id_delay";
    const $helpText = $("#message_form .field-delay .help");

    const helpText = $helpText.html().replaceAll(/\d+/g, `<a href="#" onclick="document.querySelector('${delayField}').value='$&'; return false;">$&</a>`);

    console.log(helpText);

    $helpText.html(helpText);
  });
})(django.jQuery);
