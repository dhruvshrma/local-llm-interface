document.addEventListener("DOMContentLoaded", function () {
    const modelSelect = document.getElementById("model-select");
    const initialQueryInput = document.getElementById("query-input");
    const conversationContainer = document.getElementById("response-container");
  
    initialQueryInput.addEventListener("keypress", function(event) {
      handleQuerySubmit(event, modelSelect, conversationContainer);
    });

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
}); 

function handleQuerySubmit(event, modelSelect, container) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault(); 
  
      const queryInput = event.target; 
      const model = modelSelect.value;
  
      if (!model) {
        alert("Please select a model first.");
        return;
      }
  
      const query = queryInput.value;
  
      fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: model, query: query }),
      })
      .then(async (response) => {
        const newResponseOutput = document.createElement("textarea");
        newResponseOutput.readOnly = true;
        container.appendChild(newResponseOutput);
  
        const reader = response.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = new TextDecoder().decode(value);
          newResponseOutput.value += text;
          adjustTextareaHeight(newResponseOutput);
        }
        createNewQueryInput(container, modelSelect); 
      })
      .catch((error) => {
        console.error("Error:", error);
      });
    }
  }

  function createNewQueryInput(container, modelSelect) {
    let newQueryInput = document.createElement("textarea");
    container.appendChild(newQueryInput);
    newQueryInput.focus();

    newQueryInput.addEventListener("keypress", function(event) {
      handleQuerySubmit(event, modelSelect, container);
    });
  }

  function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}
