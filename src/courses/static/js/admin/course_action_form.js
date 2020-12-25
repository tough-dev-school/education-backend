(function ($) {
  $(document).ready(() => {
    var $templateId = $(".actions input[name=template_id]");
    var $action = $(".actions select[name=action]");

    $templateId.css("display", "None");

    $action.change((e) => {
      if (e.target.value == "send_email_to_all_purchased_users") {
        $templateId.css("display", "inline-block");
        return;
      }
      $templateId.css("display", "None");
    });
  });
})(django.jQuery);
