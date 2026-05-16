(function () {
  const saveBtn = document.getElementById("save-flags-btn");
  const statusEl = document.getElementById("flags-status");
  const llmCheckbox = document.getElementById("ff-llm");
  const showTextCheckbox = document.getElementById("ff-show-text");

  if (!saveBtn || !llmCheckbox || !showTextCheckbox) {
    return;
  }

  async function saveFlags() {
    statusEl.textContent = "Saving…";
    try {
      const response = await fetch("/api/v1/feature-flags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          llm_analyzer: llmCheckbox.checked,
          show_extracted_text: showTextCheckbox.checked,
        }),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || response.statusText);
      }
      const data = await response.json();
      statusEl.textContent = `Saved. LLM: ${data.effective.llm_analyzer ? "on" : "off"}, extracted text: ${data.effective.show_extracted_text ? "on" : "off"}`;
    } catch (err) {
      statusEl.textContent = `Failed to save flags: ${err.message}`;
    }
  }

  saveBtn.addEventListener("click", saveFlags);
})();
