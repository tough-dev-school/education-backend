document.addEventListener('DOMContentLoaded', function() {
    const courseField = document.querySelector('#id_course');
    const studentField = document.querySelector('#id_student');

    courseField.addEventListener('change', function() {
        fetch(`/api/v2/courses/${courseField.value}/students/`)
            .then(response => response.json())
            .then(data => {
                studentField.innerHTML = '';
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.text = item.username;
                    studentField.appendChild(option);
                });
            });
    });
});
