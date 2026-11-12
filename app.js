const form = document.querySelector("#moderation-form");
const messageInput = document.querySelector("#message");
const charCount = document.querySelector("#char-count");
const analyzeButton = document.querySelector("#analyze-button");
const errorMessage = document.querySelector("#error-message");
const result = document.querySelector("#result");

const categoryNames = {
  safe: "Looks safe",
  harassment: "Potential harassment",
  hate: "Potential hate speech",
  violence: "Potential violence",
  sexual: "Potential sexual content",
  self_harm: "Potential self-harm content",
};

messageInput.addEventListener("input", () => {
  charCount.textContent = `${messageInput.value.length.toLocaleString()} / 2,000`;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.hidden = true;
  result.hidden = true;
  analyzeButton.disabled = true;
  analyzeButton.firstElementChild.textContent = "Analyzing...";

  try {
    const response = await fetch("/api/moderate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: messageInput.value }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Unable to analyze this message.");
    }

    document.querySelector("#result-category").textContent =
      categoryNames[data.category] || data.category;
    document.querySelector("#result-action").textContent =
      data.action === "allow" ? "Allow" : data.action === "restrict" ? "Restrict" : "Review";
    document.querySelector("#result-action").className = `action-badge action-${data.action}`;
    document.querySelector("#confidence-value").textContent =
      `${Math.round(data.confidence * 100)}%`;
    document.querySelector("#confidence-bar").style.width =
      `${Math.round(data.confidence * 100)}%`;

    const termsRow = document.querySelector("#matched-terms-row");
    const termsList = document.querySelector("#matched-terms");
    termsList.replaceChildren();
    for (const term of data.matched_terms) {
      const chip = document.createElement("span");
      chip.className = "term-chip";
      chip.textContent = term;
      termsList.append(chip);
    }
    termsRow.hidden = data.matched_terms.length === 0;
    result.hidden = false;
  } catch (error) {
    errorMessage.textContent = error.message || "Unable to connect to the moderation service.";
    errorMessage.hidden = false;
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.firstElementChild.textContent = "Analyze message";
  }
});
