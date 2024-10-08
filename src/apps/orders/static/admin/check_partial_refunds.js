(function($) {
    $(document).ready(() => {
        var noPartialRefundAvailable = ['dolyame', 'zero_price'];
        var bankId = $('#id_bank_id').val();
        var refundsGroup = $('#refunds-group');

        if (noPartialRefundAvailable.includes(bankId)) {
          setTimeout(() => {
            django.jQuery('.add-row').hide();
            var warningText = '<p style="color: darkslategray;">Частичный возврат можно делать только для заказов оплаченных через Тинькофф, Страйп или B2B</p>';
            refundsGroup.before(warningText);
          }, 1);

    }
    });
})(django.jQuery);
