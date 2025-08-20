document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadBox = document.getElementById('uploadBox');
    const resultsDiv = document.getElementById('results');

    uploadBox.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFile);

    function handleFile(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(evt) {
            const base64Image = evt.target.result;
            resultsDiv.innerHTML = "<p>Processing...</p>";

            fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64Image })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    resultsDiv.innerHTML = "<p>Error: " + data.error + "</p>";
                    return;
                }
                renderResults(data.problems);
            })
            .catch(err => {
                resultsDiv.innerHTML = "<p>Error: " + err + "</p>";
            });
        };
        reader.readAsDataURL(file);
    }

    function renderResults(problems) {
        if (!problems.length) {
            resultsDiv.innerHTML = "<p>No problems found.</p>";
            return;
        }
        let html = "<h2>Results</h2><ul>";
        problems.forEach(p => {
            const cls = p.isCorrect ? "correct" : "incorrect";
            html += `<li class="${cls}">${p.question} ${p.userAnswer} <small>(Correct: ${p.correctAnswer})</small></li>`;
        });
        html += "</ul>";
        resultsDiv.innerHTML = html;
    }
});
