// ===============================
// Chatbot Toggle
// ===============================
function toggleChatbot() {
  const chatbot = document.getElementById("chatbotBox");
  chatbot.style.display = chatbot.style.display === "block" ? "none" : "block";
}

// ===============================
// Send Message
// ===============================
function sendMessage() {
  const input = document.getElementById("userMessage");
  const message = input.value.trim();
  if (!message) return;

  const chatBody = document.getElementById("chatBody");

  // Append user message
  const userMsg = document.createElement("div");
  userMsg.className = "user-msg";
  userMsg.textContent = "🧑 You: " + message;
  chatBody.appendChild(userMsg);

  // Decide bot reply
  let reply = getBotReply(message);

  // Append bot message
  const botMsg = document.createElement("div");
  botMsg.className = "bot-msg";
  botMsg.textContent = "🤖 HealMate: " + reply;
  chatBody.appendChild(botMsg);

  // Reset input
  input.value = "";
  chatBody.scrollTop = chatBody.scrollHeight;
}

// ===============================
// Bot Reply Logic
// ===============================
function getBotReply(message) {
  message = message.toLowerCase();

  // Diet related
  if (message.includes("diet") || message.includes("food")) {
    return "Avoid ❌: Sugar, fried food, white rice. ✅ Prefer: veggies, proteins, whole grains, and 2-3L water daily 💧.";
  }

  // Calories
  if (message.includes("calorie") || message.includes("calories")) {
    return "On average, a balanced diabetic diet = 1500–2000 kcal/day depending on age, weight & activity. 🍲";
  }

  // Prediction logic explanation
  if (message.includes("how") && message.includes("work")) {
    return "I use a Machine Learning model (Logistic Regression). It studies your glucose, BMI, BP, age, and family history → then calculates your diabetes risk ✅.";
  }

  // Default reply
  return "I'm still learning 😅. Try asking about 'diet', 'calories', or 'how prediction works'.";
}
