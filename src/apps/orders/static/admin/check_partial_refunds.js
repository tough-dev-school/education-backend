(function($) {
    $(document).ready(() => {
        var partialRefundAvailable = ['stripe', 'stripe_kz', 'tinkoff_bank'];
        var bankId = $('#id_bank_id').val();
        var refundsGroup = $('#refunds-group');

        if (!partialRefundAvailable.includes(bankId)) {
          setTimeout(() => {
            refundsGroup.find('.add-row').hide();
            var warningText = '<p style="color: darkslategray;">Частичный возврат можно делать только для заказов оплаченных через Тинькофф или Страйп</p>';
            refundsGroup.before(warningText);
          }, 1);
    }
    });
})(django.jQuery);
