const elements = {
  passwordInput: document.querySelector("#passwordInput"),
  classifyBtn: document.querySelector("#classifyBtn"),
  togglePasswordBtn: document.querySelector("#togglePasswordBtn"),
  lengthInput: document.querySelector("#lengthInput"),
  upperInput: document.querySelector("#upperInput"),
  lowerInput: document.querySelector("#lowerInput"),
  digitsInput: document.querySelector("#digitsInput"),
  symbolsInput: document.querySelector("#symbolsInput"),
  generateBtn: document.querySelector("#generateBtn"),
  generatedOutput: document.querySelector("#generatedOutput"),
  copyGeneratedBtn: document.querySelector("#copyGeneratedBtn"),
  fruitInput: document.querySelector("#fruitInput"),
  streetInput: document.querySelector("#streetInput"),
  numberInput: document.querySelector("#numberInput"),
  passwordError: document.querySelector("#passwordError"),
  fruitError: document.querySelector("#fruitError"),
  streetError: document.querySelector("#streetError"),
  numberError: document.querySelector("#numberError"),
  personalizedBtn: document.querySelector("#personalizedBtn"),
  personalizedOutput: document.querySelector("#personalizedOutput"),
  copyPersonalizedBtn: document.querySelector("#copyPersonalizedBtn"),
  labelOutput: document.querySelector("#labelOutput"),
  scoreMeter: document.querySelector("#scoreMeter"),
  scoreOutput: document.querySelector("#scoreOutput"),
  entropyOutput: document.querySelector("#entropyOutput"),
  lengthOutput: document.querySelector("#lengthOutput"),
  reasonsOutput: document.querySelector("#reasonsOutput"),
  suggestionsOutput: document.querySelector("#suggestionsOutput")
};

const PASSWORD_MAX_LENGTH = 256;
const WORD_MAX_LENGTH = 40;

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function renderList(target, items, emptyText) {
  target.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    target.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  });
}

function colorForScore(score) {
  if (score >= 90) return "#157347";
  if (score >= 70) return "#0f766e";
  if (score >= 50) return "#b45309";
  if (score >= 30) return "#c2410c";
  return "#b42318";
}

function keepLettersAndSpaces(input) {
  const original = input.value;
  input.value = original.replace(/[^A-Za-z ]/g, "");
  return original !== input.value;
}

function keepLetters(input) {
  const original = input.value;
  input.value = original.replace(/[^A-Za-z]/g, "");
  return original !== input.value;
}

function keepDigits(input) {
  const original = input.value;
  input.value = original.replace(/\D/g, "");
  return original !== input.value;
}

function setFieldError(input, errorElement, message) {
  errorElement.textContent = message;
  input.classList.toggle("invalid", Boolean(message));
}

function setCopyReady(button, isReady) {
  button.disabled = !isReady;
  button.textContent = "Copy";
}

async function copyTextFromOutput(outputElement, button) {
  const text = outputElement.textContent.trim();
  if (!text) return;

  await navigator.clipboard.writeText(text);
  button.textContent = "Copied";
  window.setTimeout(() => {
    if (!button.disabled) {
      button.textContent = "Copy";
    }
  }, 1400);
}

function validatePasswordInput() {
  const password = elements.passwordInput.value;
  if (!password) {
    setFieldError(elements.passwordInput, elements.passwordError, "Password is required");
    return null;
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    setFieldError(elements.passwordInput, elements.passwordError, "Maximum 256 characters");
    return null;
  }

  setFieldError(elements.passwordInput, elements.passwordError, "");
  return password;
}

function validateWordInput(input, errorElement, fieldName) {
  const value = input.value.trim();
  if (!value) {
    setFieldError(input, errorElement, `${fieldName} is required`);
    return null;
  }
  if (value.length > WORD_MAX_LENGTH) {
    setFieldError(input, errorElement, "Maximum 40 characters");
    return null;
  }
  if (!/^[A-Za-z ]+$/.test(value)) {
    setFieldError(input, errorElement, "Letters only");
    return null;
  }

  setFieldError(input, errorElement, "");
  return value;
}

function validateLettersInput(input, errorElement, fieldName) {
  const value = input.value.trim();
  if (!value) {
    setFieldError(input, errorElement, `${fieldName} is required`);
    return null;
  }
  if (value.length > WORD_MAX_LENGTH) {
    setFieldError(input, errorElement, "Maximum 40 characters");
    return null;
  }
  if (!/^[A-Za-z]+$/.test(value)) {
    setFieldError(input, errorElement, "Letters only");
    return null;
  }

  setFieldError(input, errorElement, "");
  return value;
}

function validateNumberInput() {
  const number = elements.numberInput.value.trim();
  if (!number) {
    setFieldError(elements.numberInput, elements.numberError, "Number is required");
    return null;
  }
  if (!/^\d+$/.test(number)) {
    setFieldError(elements.numberInput, elements.numberError, "Numbers only");
    return null;
  }

  setFieldError(elements.numberInput, elements.numberError, "");
  return number;
}

function validatePersonalizedInputs() {
  const validFruit = validateLettersInput(elements.fruitInput, elements.fruitError, "Fruit");
  const validStreet = validateWordInput(elements.streetInput, elements.streetError, "Street");
  const validNumber = validateNumberInput();

  if (!validFruit || !validStreet || !validNumber) {
    return null;
  }

  return { fruit: validFruit, street: validStreet, number: validNumber };
}

function renderClassification(result) {
  const score = Number(result.score || 0);
  const color = colorForScore(score);
  elements.labelOutput.textContent = result.label || "unknown";
  elements.labelOutput.style.color = color;
  elements.labelOutput.style.background = `${color}18`;
  elements.scoreMeter.style.width = `${score}%`;
  elements.scoreMeter.style.background = color;
  elements.scoreOutput.textContent = `${score}/100`;
  elements.entropyOutput.textContent = `${result.entropy || 0} bits`;
  elements.lengthOutput.textContent = result.length || 0;

  renderList(elements.reasonsOutput, result.reasons, "No reasons yet");
  renderList(elements.suggestionsOutput, result.suggestions, "No suggestions yet");
}

function renderError(message) {
  elements.labelOutput.textContent = "Error";
  elements.labelOutput.style.color = "#b42318";
  elements.labelOutput.style.background = "#b4231818";
  elements.scoreMeter.style.width = "0%";
  elements.scoreOutput.textContent = "0/100";
  elements.entropyOutput.textContent = "0";
  elements.lengthOutput.textContent = "0";
  renderList(elements.reasonsOutput, [message], "");
  renderList(elements.suggestionsOutput, [], "No suggestions yet");
  elements.reasonsOutput.firstElementChild.className = "error";
}

elements.classifyBtn.addEventListener("click", async () => {
  try {
    const password = validatePasswordInput();
    if (!password) return;

    const result = await postJson("/classify", {
      password
    });
    renderClassification(result);
  } catch (error) {
    renderError(error.message);
  }
});

elements.passwordInput.addEventListener("input", () => {
  if (elements.passwordInput.value.length <= PASSWORD_MAX_LENGTH) {
    setFieldError(elements.passwordInput, elements.passwordError, "");
  }
});

elements.togglePasswordBtn.addEventListener("click", () => {
  const hidden = elements.passwordInput.type === "password";
  elements.passwordInput.type = hidden ? "text" : "password";
  elements.togglePasswordBtn.textContent = hidden ? "Hide" : "Show";
});

elements.generateBtn.addEventListener("click", async () => {
  try {
    const result = await postJson("/generate", {
      length: elements.lengthInput.value,
      use_upper: elements.upperInput.checked,
      use_lower: elements.lowerInput.checked,
      use_digits: elements.digitsInput.checked,
      use_symbols: elements.symbolsInput.checked
    });
    elements.generatedOutput.textContent = result.password;
    setCopyReady(elements.copyGeneratedBtn, true);
    renderClassification(result.classification);
  } catch (error) {
    renderError(error.message);
  }
});

elements.fruitInput.addEventListener("input", () => {
  const removedInvalid = keepLetters(elements.fruitInput);
  if (removedInvalid) {
    setFieldError(elements.fruitInput, elements.fruitError, "Letters only");
    return;
  }
  validateLettersInput(elements.fruitInput, elements.fruitError, "Fruit");
});

elements.streetInput.addEventListener("input", () => {
  const removedInvalid = keepLettersAndSpaces(elements.streetInput);
  if (removedInvalid) {
    setFieldError(elements.streetInput, elements.streetError, "Letters only");
    return;
  }
  validateWordInput(elements.streetInput, elements.streetError, "Street");
});

elements.numberInput.addEventListener("input", () => {
  const removedInvalid = keepDigits(elements.numberInput);
  if (removedInvalid) {
    setFieldError(elements.numberInput, elements.numberError, "Numbers only");
    return;
  }
  validateNumberInput();
});

elements.personalizedBtn.addEventListener("click", async () => {
  try {
    const payload = validatePersonalizedInputs();
    if (!payload) return;

    const result = await postJson("/generate-personalized", payload);
    elements.personalizedOutput.textContent = result.password;
    setCopyReady(elements.copyPersonalizedBtn, true);
    renderClassification(result.classification);
  } catch (error) {
    renderError(error.message);
  }
});

elements.copyGeneratedBtn.addEventListener("click", async () => {
  try {
    await copyTextFromOutput(elements.generatedOutput, elements.copyGeneratedBtn);
  } catch (error) {
    elements.copyGeneratedBtn.textContent = "Failed";
  }
});

elements.copyPersonalizedBtn.addEventListener("click", async () => {
  try {
    await copyTextFromOutput(elements.personalizedOutput, elements.copyPersonalizedBtn);
  } catch (error) {
    elements.copyPersonalizedBtn.textContent = "Failed";
  }
});
