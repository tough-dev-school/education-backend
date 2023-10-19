(function($) {
  $(document).ready(() => {
    var $chain = $('#message_form select#id_chain');
    var $parent = $('#message_form select#id_parent');

    function updateMessageSelector() {
      const chainLabel = $chain.find('option:checked')[0].label;
      const selectedParentLabel = $parent.find('option:checked')[0].label;

      if (!selectedParentLabel.startsWith(chainLabel)) {
        $parent.find('option:first').prop('selected', true);
      }

      $parent.find('option').each(function() {
        if (this.label.startsWith(chainLabel)) {
          $(this).attr('disabled', false);
        } else {
          $(this).attr('disabled', true);
        }
      });
    }
    $chain.on('change', updateMessageSelector);

    updateMessageSelector();
  });
})(django.jQuery);
