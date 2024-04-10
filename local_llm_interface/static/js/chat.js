document.addEventListener("DOMContentLoaded", function () {
    const modelSelect = document.getElementById("model-select");
    const queryInput = document.getElementById("query-input");
    // const submitBtn = document.getElementById("submit-btn");
    const responseOutput = document.getElementById("response-output");

    fetch("/api/models")
        .then((response) => response.json())
        .then((data) => {
            const modelSelect = document.getElementById("model-select");
            data.models.forEach((model) => {
                const option = document.createElement("option");
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        })
        .catch((error) => {
            console.error("Could not load models:", error);
        });

    modelSelect.onchange = function () {
        modelSelect.disabled = !this.value;
    };

    queryInput.addEventListener("keypress", function(e){
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!modelSelect.value) {
                alert("Please select a model first!");
                return;
            }
        }
        const model = modelSelect.value;
        const query = queryInput.value;

        // Disable form elements during request
        // submitBtn.disabled = true;
        modelSelect.disabled = true;
        queryInput.disabled = true;

        // Fetch API setup for streaming response
        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model: model, query: query }),
        })
            .then(async (response) => {
                const reader = response.body.getReader();
                // let newResponseOutput = document.createElement("textarea");
                // newResponseOutput.readOnly = true;

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const text = new TextDecoder().decode(value);
                    responseOutput.value += text; // Append streamed response

                    responseOutput.style.height = "auto";
                    responseOutput.style.height = responseOutput.scrollHeight + "px"; // Auto-expand textarea
                }
                createNewQueryInput(responseContainer, modelSelect);
                // Re-enable form elements after streaming ends
                // submitBtn.disabled = false;
                modelSelect.disabled = false;
                queryInput.disabled = false;
            })
            .catch((error) => {
                console.error("Error:", error);
                // Re-enable form elements in case of error
                // submitBtn.disabled = false;
                modelSelect.disabled = false;
                queryInput.disabled = false;
            });
    });
});

function createNewQueryInput(container, modelSelect){
    let newQueryInput = document.createElement("textarea");
    newQueryInput.placeholder = "Type your message here...";
    newQueryInput.id = "query-input";
    container.appendChild(newQueryInput);
    newQueryInput.focus();
    
}