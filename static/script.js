// Toggle Dark/Light Mode
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("dark-mode", document.body.classList.contains("dark-mode"));
}

// Show/Hide Voice Modal
function showVoiceModal(show = true) {
  const modal = document.getElementById("voiceModal");
  modal.classList.toggle("hidden", !show);
}

// Voice Recognition Handler
function startVoiceRecognition() {
  showVoiceModal(true);
  const input = document.getElementById("productInput");

  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
  };

  recognition.onerror = (event) => {
    console.error("Voice recognition error:", event.error);
    showVoiceModal(false);
  };

  recognition.onend = () => {
    showVoiceModal(false);
    if (input.value.trim()) {
      searchProduct();
    }
  };

  recognition.start();
}

// Main Search Function (✅ IndiaMART Added)
async function searchProduct() {
  const query = document.getElementById("productInput").value.trim();
  const amazonDiv = document.getElementById("amazonResults");
  const flipkartDiv = document.getElementById("flipkartResults");
  const meeshoDiv = document.getElementById("meeshoResults");
  const indiamartDiv = document.getElementById("indiamartResults"); // ✅ IndiaMART
  const recDiv = document.getElementById("recommendations");
  const smartRecDiv = document.getElementById("smart-recommendations");

  // Reset previous results
  amazonDiv.innerHTML = "<h2>Amazon</h2><div class='loader'>🔄 Searching...</div>";
  flipkartDiv.innerHTML = "<h2>Flipkart</h2><div class='loader'>🔄 Searching...</div>";
  meeshoDiv.innerHTML = "<h2>Meesho</h2><div class='loader'>🔄 Searching...</div>";
  indiamartDiv.innerHTML = "<h2>IndiaMART</h2><div class='loader'>🔄 Searching...</div>";
  recDiv.innerHTML = "";
  smartRecDiv.innerHTML = "";

  if (!query) {
    showError(amazonDiv, "Please enter a product name");
    showError(flipkartDiv, "Please enter a product name");
    if (meeshoDiv) showError(meeshoDiv, "Please enter a product name");
    if (indiamartDiv) showError(indiamartDiv, "Please enter a product name");
    return;
  }

  // 🔽 Save to Search History (Added)
  saveToHistory(query);

  try {
    const response = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();
    console.log("🔁 Data received:", data);

    displayResults(amazonDiv, "Amazon", data.amazon, data.errors?.amazon);
    displayResults(flipkartDiv, "Flipkart", data.flipkart, data.errors?.flipkart);
    displayResults(meeshoDiv, "Meesho", data.meesho, data.errors?.meesho);
    displayResults(indiamartDiv, "IndiaMART", data.indiamart, data.errors?.indiamart);

    if (data.recommendations?.length) {
      displayRecommendations(recDiv, smartRecDiv, data.recommendations);
    }

  } catch (err) {
    console.error("Search error:", err);
    showError(amazonDiv, "❌ Failed to load results. Please try again.");
    showError(flipkartDiv, "❌ Failed to load results. Please try again.");
    showError(meeshoDiv, "❌ Failed to load results. Please try again.");
    showError(indiamartDiv, "❌ Failed to load results. Please try again.");
  }
}

// Display Results Function
function displayResults(container, siteName, items, error) {
  container.innerHTML = `<h2>${siteName}</h2>`;

  if (error) {
    container.innerHTML += `<div class="error">⚠️ ${error}</div>`;
    return;
  }

  if (!items?.length) {
    container.innerHTML += `<div class="no-results">😕 No products found.</div>`;
    return;
  }

  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "result-item";
    div.innerHTML = `
      <div class="result-image-container">
        <img src="${item.image || 'https://placehold.co/150x150?text=No+Image'}" 
             alt="${item.title}" 
             class="result-image"
             onerror="this.src='https://placehold.co/150x150?text=Image+Error'">
      </div>
      <div class="result-details">
        <a href="${item.link}" target="_blank" class="result-title">${item.title}</a>
        <div class="price-rating">
          <span class="price">${item.price || 'N/A'}</span>
          ${item.rating ? `<span class="rating">⭐ ${item.rating}</span>` : ''}
        </div>
      </div>
    `;
    container.appendChild(div);
  });
}

// Show Recommendations
function displayRecommendations(recDiv, smartRecDiv, recommendations) {
  recDiv.innerHTML = "<h3>🧠 Smart Recommendations</h3>";
  smartRecDiv.innerHTML = "<h3>🛍️ Related Products</h3>";

  recommendations.forEach(rec => {
    const textItem = document.createElement("div");
    textItem.className = "recommend-item";
    textItem.textContent = `✅ ${rec.name}`;
    recDiv.appendChild(textItem);

    const card = document.createElement("div");
    card.className = "recommend-card";
    card.innerHTML = `
      <img src="${rec.image || 'https://placehold.co/100x100?text=No+Image'}" 
           alt="${rec.name}" 
           onerror="this.src='https://placehold.co/100x100?text=Error'">
      <p>${rec.name}</p>
    `;
    smartRecDiv.appendChild(card);
  });
}

// Display Error Message
function showError(container, message) {
  container.innerHTML += `<div class="error">${message}</div>`;
}

// Init Dark Mode
function initDarkMode() {
  const isDark = localStorage.getItem("dark-mode") === "true";
  if (isDark) {
    document.body.classList.add("dark-mode");
    const toggle = document.getElementById("darkModeToggle");
    if (toggle) toggle.checked = true;
  }
}

// 🔽 Search History Feature - START
function saveToHistory(query) {
  let history = JSON.parse(localStorage.getItem("search-history")) || [];
  if (!history.includes(query)) {
    history.unshift(query);
    if (history.length > 20) history.pop();
    localStorage.setItem("search-history", JSON.stringify(history));
    renderSearchHistory();
  }
}

function renderSearchHistory() {
  const historyList = document.getElementById("searchHistory");
  const history = JSON.parse(localStorage.getItem("search-history")) || [];
  historyList.innerHTML = "";

  history.forEach((item, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="history-text" onclick="fillFromHistory('${item}')">${item}</span>
      <button class="delete-btn" onclick="deleteFromHistory(${index})">❌</button>
    `;
    historyList.appendChild(li);
  });
}

function fillFromHistory(query) {
  document.getElementById("productInput").value = query;
  searchProduct();
}

function deleteFromHistory(index) {
  let history = JSON.parse(localStorage.getItem("search-history")) || [];
  history.splice(index, 1);
  localStorage.setItem("search-history", JSON.stringify(history));
  renderSearchHistory();
}

function clearSearchHistory() {
  localStorage.removeItem("search-history");
  renderSearchHistory();
}
// 🔼 Search History Feature - END

// On Page Load
document.addEventListener("DOMContentLoaded", () => {
  // Initialize Dark Mode and search history
  initDarkMode();
  renderSearchHistory(); // 🔄 Initialize Search History on load

  // Dark Mode toggle event listener
  const toggle = document.getElementById("darkModeToggle");
  toggle?.addEventListener("change", toggleDarkMode);

  // Product search event listener
  const input = document.getElementById("productInput");
  input?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchProduct();
  });

  // Sidebar toggle functionality
  const toggleButton = document.getElementById("toggleButton");
  const sidebar = document.getElementById("leftSidebar");

  toggleButton.addEventListener("click", function () {
    sidebar.classList.toggle("show");
  });

  // Close sidebar when clicking outside (on mobile only)
  document.addEventListener("click", function (event) {
    const isClickInsideSidebar = sidebar.contains(event.target);
    const isClickOnToggle = toggleButton.contains(event.target);

    if (!isClickInsideSidebar && !isClickOnToggle && sidebar.classList.contains("show")) {
      sidebar.classList.remove("show");
    }
  });

  // Mobile search toggle functionality
  const toggleBtn = document.querySelector(".mobile-search-toggle");
  const searchBox = document.querySelector(".search-box");

  toggleBtn.addEventListener("click", function () {
    searchBox.classList.toggle("active");
  });
});

