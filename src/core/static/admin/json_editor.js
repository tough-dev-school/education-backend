(function() {
    function validateJSON(widget) {
        try {
            JSON.parse(widget.value);
            widget.classList.remove('app-json-editor--error');
            return true;
        } catch (error) {
            widget.classList.add('app-json-editor--error');
            return false;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        const widgets = document.querySelectorAll('.app-json-editor');
        widgets.forEach((widget) => {
            // Format initial JSON
            try {
                const parsed = JSON.parse(widget.value);
                const formatted = JSON.stringify(parsed, null, 4);
                widget.value = formatted;
                widget.classList.remove('errornote');
            } catch (error) {
                widget.classList.add('errornote');
            }

            // Validate on every keypress
            widget.addEventListener('input', function() {
                validateJSON(widget);
            });
        });
    });
})();
