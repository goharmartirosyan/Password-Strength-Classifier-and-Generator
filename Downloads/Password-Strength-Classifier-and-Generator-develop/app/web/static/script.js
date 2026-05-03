const passwordInput = document.getElementById("passwordInput");
const classifyBtn = document.getElementById("classifyBtn");
const togglePasswordBtn = document.getElementById("togglePasswordBtn");
const lengthInput = document.getElementById("lengthInput");
const upperInput = document.getElementById("upperInput");
const lowerInput = document.getElementById("lowerInput");
const digitsInput = document.getElementById("digitsInput");
const symbolsInput = document.getElementById("symbolsInput");
const generateBtn = document.getElementById("generateBtn");
const generatedOutput = document.getElementById("generatedOutput");
const copyGeneratedBtn = document.getElementById("copyGeneratedBtn");
const fruitInput = document.getElementById("fruitInput");
const streetInput = document.getElementById("streetInput");
const numberInput = document.getElementById("numberInput");
const passwordError = document.getElementById("passwordError");
const fruitError = document.getElementById("fruitError");
const streetError = document.getElementById("streetError");
const numberError = document.getElementById("numberError");
const personalizedBtn = document.getElementById("personalizedBtn");
const personalizedOutput = document.getElementById("personalizedOutput");
const copyPersonalizedBtn = document.getElementById("copyPersonalizedBtn");
const labelOutput = document.getElementById("labelOutput");
const scoreMeter = document.getElementById("scoreMeter");
const scoreOutput = document.getElementById("scoreOutput");
const entropyOutput = document.getElementById("entropyOutput");
const lengthOutput = document.getElementById("lengthOutput");
const reasonsOutput = document.getElementById("reasonsOutput");
const suggestionsOutput = document.getElementById("suggestionsOutput");

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

function setFieldError(input, errorEl, message) {
  errorEl.textContent = message;
  input.classList.toggle("invalid", Boolean(message));
}

function setCopyReady(button, isReady) {
  button.disabled = !isReady;
  button.textContent = "Copy";
}

async function copyTextFromOutput(outputEl, button) {
  const text = outputEl.textContent.trim();
  if (!text) return;

  await navigator.clipboard.writeText(text);
  button.textContent = "Copied";
  setTimeout(() => {
    if (!button.disabled) {
      button.textContent = "Copy";
    }
  }, 1400);
}

function validatePasswordInput() {
  const password = passwordInput.value;
  if (!password) {
    setFieldError(passwordInput, passwordError, "Password is required");
    return null;
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    setFieldError(passwordInput, passwordError, "Maximum 256 characters");
    return null;
  }
  setFieldError(passwordInput, passwordError, "");
  return password;
}

function validateWordInput(input, errorEl, fieldName) {
  const value = input.value.trim();
  if (!value) {
    setFieldError(input, errorEl, `${fieldName} is required`);
    return null;
  }
  if (value.length > WORD_MAX_LENGTH) {
    setFieldError(input, errorEl, "Maximum 40 characters");
    return null;
  }
  if (!/^[A-Za-z ]+$/.test(value)) {
    setFieldError(input, errorEl, "Letters only");
    return null;
  }
  setFieldError(input, errorEl, "");
  return value;
}

function validateLettersInput(input, errorEl, fieldName) {
  const value = input.value.trim();
  if (!value) {
    setFieldError(input, errorEl, `${fieldName} is required`);
    return null;
  }
  if (value.length > WORD_MAX_LENGTH) {
    setFieldError(input, errorEl, "Maximum 40 characters");
    return null;
  }
  if (!/^[A-Za-z]+$/.test(value)) {
    setFieldError(input, errorEl, "Letters only");
    return null;
  }
  setFieldError(input, errorEl, "");
  return value;
}

function validateNumberInput() {
  const number = numberInput.value.trim();
  if (!number) {
    setFieldError(numberInput, numberError, "Number is required");
    return null;
  }
  if (!/^\d+$/.test(number)) {
    setFieldError(numberInput, numberError, "Numbers only");
    return null;
  }
  setFieldError(numberInput, numberError, "");
  return number;
}

function validatePersonalizedInputs() {
  const validFruit = validateLettersInput(fruitInput, fruitError, "Fruit");
  const validStreet = validateWordInput(streetInput, streetError, "Street");
  const validNumber = validateNumberInput();

  if (!validFruit || !validStreet || !validNumber) return null;

  return { fruit: validFruit, street: validStreet, number: validNumber };
}

function renderClassification(result) {
  const score = Number(result.score || 0);
  const color = colorForScore(score);
  labelOutput.textContent = result.label || "unknown";
  labelOutput.style.color = color;
  labelOutput.style.background = `${color}18`;
  scoreMeter.style.width = `${score}%`;
  scoreMeter.style.background = color;
  scoreOutput.textContent = `${score}/100`;
  entropyOutput.textContent = `${result.entropy || 0} bits`;
  lengthOutput.textContent = result.length || 0;

  renderList(reasonsOutput, result.reasons, "No reasons yet");
  renderList(suggestionsOutput, result.suggestions, "No suggestions yet");
}

function renderError(message) {
  labelOutput.textContent = "Error";
  labelOutput.style.color = "#b42318";
  labelOutput.style.background = "#b4231818";
  scoreMeter.style.width = "0%";
  scoreOutput.textContent = "0/100";
  entropyOutput.textContent = "0";
  lengthOutput.textContent = "0";
  renderList(reasonsOutput, [message], "");
  renderList(suggestionsOutput, [], "No suggestions yet");
  reasonsOutput.firstElementChild.className = "error";
}

classifyBtn.addEventListener("click", async () => {
  try {
    const password = validatePasswordInput();
    if (!password) return;

    const result = await postJson("/classify", { password });
    renderClassification(result);
  } catch (err) {
    renderError(err.message);
  }
});

passwordInput.addEventListener("input", () => {
  if (passwordInput.value.length <= PASSWORD_MAX_LENGTH) {
    setFieldError(passwordInput, passwordError, "");
  }
});

togglePasswordBtn.addEventListener("click", () => {
  const hidden = passwordInput.type === "password";
  passwordInput.type = hidden ? "text" : "password";
  togglePasswordBtn.textContent = hidden ? "Hide" : "Show";
});

generateBtn.addEventListener("click", async () => {
  try {
    const result = await postJson("/generate", {
      length: lengthInput.value,
      use_upper: upperInput.checked,
      use_lower: lowerInput.checked,
      use_digits: digitsInput.checked,
      use_symbols: symbolsInput.checked
    });
    generatedOutput.textContent = result.password;
    setCopyReady(copyGeneratedBtn, true);
    renderClassification(result.classification);
  } catch (err) {
    renderError(err.message);
  }
});

fruitInput.addEventListener("input", () => {
  const removedInvalid = keepLetters(fruitInput);
  if (removedInvalid) {
    setFieldError(fruitInput, fruitError, "Letters only");
    return;
  }
  validateLettersInput(fruitInput, fruitError, "Fruit");
});

streetInput.addEventListener("input", () => {
  const removedInvalid = keepLettersAndSpaces(streetInput);
  if (removedInvalid) {
    setFieldError(streetInput, streetError, "Letters only");
    return;
  }
  validateWordInput(streetInput, streetError, "Street");
});

numberInput.addEventListener("input", () => {
  const removedInvalid = keepDigits(numberInput);
  if (removedInvalid) {
    setFieldError(numberInput, numberError, "Numbers only");
    return;
  }
  validateNumberInput();
});

personalizedBtn.addEventListener("click", async () => {
  try {
    const payload = validatePersonalizedInputs();
    if (!payload) return;

    const result = await postJson("/generate-personalized", payload);
    personalizedOutput.textContent = result.password;
    setCopyReady(copyPersonalizedBtn, true);
    renderClassification(result.classification);
  } catch (err) {
    renderError(err.message);
  }
});

copyGeneratedBtn.addEventListener("click", async () => {
  try {
    await copyTextFromOutput(generatedOutput, copyGeneratedBtn);
  } catch {
    copyGeneratedBtn.textContent = "Failed";
  }
});

copyPersonalizedBtn.addEventListener("click", async () => {
  try {
    await copyTextFromOutput(personalizedOutput, copyPersonalizedBtn);
  } catch {
    copyPersonalizedBtn.textContent = "Failed";
  }
});
