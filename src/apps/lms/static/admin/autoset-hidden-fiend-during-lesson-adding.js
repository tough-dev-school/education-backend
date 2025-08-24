(function($) {
  $(document).ready(() => {
    const $table = $('#lesson_set-group table');
    
    if ($table.length === 0) {
      return;
    }

    // Watch for new rows being added
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.tagName === 'TR' && !$(node).hasClass('has_original')) {
            // This is a newly added row - check the hidden field
            $(node).find('td.field-hidden input[type="checkbox"]').prop('checked', true);
          }
        });
      });
    });

    observer.observe($table[0], { childList: true, subtree: true });
  });
})(django.jQuery);