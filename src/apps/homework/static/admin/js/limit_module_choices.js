(function ($) {
  $(document).ready(() => {
    var $course = $("#question_form select#id_course");
    var $module = $("#question_form select#id_module");
    var $lesson = $("#question_form select#id_lesson");

    function updateModuleSelector() {
      const courseLabel = $course.find("option:checked")[0].label;
      const selectedModuleLabel = $module.find("option:checked")[0].label;

      if (courseLabel == '---------') { // это None по-джанговски
        $module.hide();
      } else{
        $module.show();
      }

      if (!selectedModuleLabel.includes(courseLabel)) {
        $module.find("option:first").prop("selected", true);
      }

      $module.find("option").each(function () {
        if (this.label.includes(courseLabel)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    }

    function updateLessonSelector() {
      const moduleLabel = $module.find("option:checked")[0].label;
      const selectedLessonLabel = $lesson.find("option:checked")[0].label;

      if (moduleLabel == '---------') { // это None по-джанговски
        $lesson.hide();
      } else{
        $lesson.show();
      }

      if (!selectedLessonLabel.includes(moduleLabel)) {
        $lesson.find("option:first").prop("selected", true);
      }

      $lesson.find("option").each(function () {
        if (this.label.includes(moduleLabel)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    }

    $course.on("change", updateModuleSelector);
    $module.on("change", updateLessonSelector);

    updateModuleSelector();
    updateLessonSelector();
  });
})(django.jQuery);
