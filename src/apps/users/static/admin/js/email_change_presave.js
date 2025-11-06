(function ($) {
  $(document).ready(() => {
    var $emailInput = $("#id_email");
    var originalEmail = $emailInput.val();
    var warningElement = null;
    var okElement = null;
    var checkTimeout = null;

    // Email validation regex
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function removeWarning() {
      if (warningElement) {
        warningElement.remove();
        warningElement = null;
      }
      if (okElement) {
        okElement.remove();
        okElement = null;
      }
    }

    function showWarning(message) {
      removeWarning();
      warningElement = $('<p class="email-change-presave__notification">' + message + "</p>");
      $emailInput.after(warningElement);
    }

    function highlightOk(message) {
      removeWarning();
      okElement = $('<p class="email-change-presave__notification">' + message + "</p>");
      $emailInput.after(okElement);
    }

    function checkEmailExists(email) {
      $.ajax({
        url: "/api/v2/users/?email=" + encodeURIComponent(email),
        method: "GET",
        success: function (response) {
          if (response.results && response.results.length > 0) {
            showWarning("Пользователь с таким email уже существует! Если сохранить — данные текущего пользователя приклеются к нему");
          } else {
            highlightOk("Email свободен, можно менять");
          }
        },
        error: function (xhr) {
          if (xhr.status === 403 || xhr.status === 401) {
            // User doesn't have permission to check - silently ignore
            removeWarning();
          } else {
            showWarning("Ошибка проверки email", true);
          }
        },
      });
    }

    $emailInput.on("input", function () {
      var currentEmail = $(this).val().trim();

      // Clear any pending check
      if (checkTimeout) {
        clearTimeout(checkTimeout);
      }

      removeWarning();

      if (emailRegex.test(currentEmail) && currentEmail !== originalEmail) {
        // Debounce the API call by 500ms
        checkTimeout = setTimeout(function () {
          checkEmailExists(currentEmail);
        }, 500);
      }
    });
  });
})(django.jQuery);
