document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  try {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map((popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl))
  } catch (e) {
    console.log("Bootstrap components initialization error:", e)
  }

  // Feature cards animation on scroll
  const featureCards = document.querySelectorAll(".feature-card")
  if (featureCards.length > 0) {
    window.addEventListener("scroll", () => {
      featureCards.forEach((card) => {
        const cardPosition = card.getBoundingClientRect().top
        const screenPosition = window.innerHeight / 1.3

        if (cardPosition < screenPosition) {
          card.classList.add("animate-fadeInUp")
        }
      })
    })
  }

  // File upload preview
  const fileInput = document.getElementById("mri-upload")
  const previewContainer = document.getElementById("preview-container")
  const previewImage = document.getElementById("preview-image")

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const file = this.files[0]
      if (file) {
        const reader = new FileReader()

        reader.onload = (e) => {
          previewImage.src = e.target.result
          previewContainer.classList.remove("d-none")
        }

        reader.readAsDataURL(file)
      }
    })
  }

  // Prediction form submission
  const predictionForm = document.getElementById("prediction-form")
  const resultContainer = document.getElementById("result-container")
  const loadingSpinner = document.getElementById("loading-spinner")

  if (predictionForm) {
    predictionForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const formData = new FormData(this)

      // Show loading spinner
      loadingSpinner.classList.remove("d-none")
      resultContainer.classList.add("d-none")

      fetch("/predict", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loading spinner
          loadingSpinner.classList.add("d-none")

          if (data.error) {
            alert(data.error)
            return
          }

          // Display result
          document.getElementById("result-image").src = "/static/" + data.image_path
          document.getElementById("result-type").textContent = data.prediction
          document.getElementById("result-confidence").textContent = `Confidence: ${data.confidence.toFixed(2)}%`

          // Store prediction for chatbot and health plan
          localStorage.setItem("tumorType", data.prediction)

          // Show result container
          resultContainer.classList.remove("d-none")

          // Enable view health plan button
          document.getElementById("view-health-plan").disabled = false
        })
        .catch((error) => {
          loadingSpinner.classList.add("d-none")
          console.error("Error:", error)
          alert("An error occurred during prediction. Please try again.")
        })
    })
  }

  // View health plan button
  const viewHealthPlanBtn = document.getElementById("view-health-plan")
  if (viewHealthPlanBtn) {
    viewHealthPlanBtn.addEventListener("click", () => {
      window.location.href = "/health-plan"
    })
  }

  // Health plan page
  const healthPlanContainer = document.getElementById("health-plan-container")
  if (healthPlanContainer) {
    const tumorType = localStorage.getItem("tumorType") || "No tumor"
    document.getElementById("tumor-type").textContent = tumorType

    // Fetch health plan data
    fetch(`/get-health-plan/${tumorType}`)
      .then((response) => response.json())
      .then((data) => {
        // Update tumor type name if available
        if (data.tumorTypeName) {
          document.getElementById("tumor-type").textContent = data.tumorTypeName
        }

        // Diet section
        document.getElementById("diet-overview").textContent =
          data.dietOverview || "No specific diet overview available."

        const recommendedFoodsList = document.getElementById("recommended-foods")
        const foodsToAvoidList = document.getElementById("foods-to-avoid")

        // Clear existing lists
        recommendedFoodsList.innerHTML = ""
        foodsToAvoidList.innerHTML = ""

        // Populate recommended foods list
        if (data.recommendedFoods && data.recommendedFoods.length > 0) {
          data.recommendedFoods.forEach((item) => {
            const li = document.createElement("li")
            li.textContent = item
            recommendedFoodsList.appendChild(li)
          })
        } else {
          const li = document.createElement("li")
          li.textContent = "No specific food recommendations available."
          recommendedFoodsList.appendChild(li)
        }

        // Populate foods to avoid list
        if (data.foodsToAvoid && data.foodsToAvoid.length > 0) {
          data.foodsToAvoid.forEach((item) => {
            const li = document.createElement("li")
            li.textContent = item
            foodsToAvoidList.appendChild(li)
          })
        } else {
          const li = document.createElement("li")
          li.textContent = "No specific foods to avoid listed."
          foodsToAvoidList.appendChild(li)
        }

        // Treatment section
        document.getElementById("treatment-overview").textContent =
          data.treatmentOverview || "No specific treatment overview available."
        document.getElementById("surgery-description").textContent =
          data.surgeryDescription || "No specific surgery information available."
        document.getElementById("radiation-description").textContent =
          data.radiationDescription || "No specific radiation therapy information available."
        document.getElementById("chemotherapy-description").textContent =
          data.chemotherapyDescription || "No specific chemotherapy information available."
        document.getElementById("targeted-therapy").textContent =
          data.targetedTherapy || "No specific targeted therapy information available."
        document.getElementById("priority-levels").textContent =
          data.priorityLevels || "No specific priority information available."
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("An error occurred while fetching health plan data.")
      })

    // Print functionality
    const printButton = document.getElementById("print-plan")
    if (printButton) {
      printButton.addEventListener("click", () => {
        window.print()
      })
    }
  }

  // Chatbot functionality
  const chatForm = document.getElementById("chat-form")
  const chatInput = document.getElementById("chat-input")
  const chatBox = document.getElementById("chat-box")

  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault()

      const message = chatInput.value.trim()
      if (!message) return

      // Add user message to chat
      addMessageToChat("user", message)

      // Clear input
      chatInput.value = ""

      // Get tumor type from localStorage
      const tumorType = localStorage.getItem("tumorType") || "No tumor"

      // Send message to server
      fetch("/chatbot-query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          tumor_type: tumorType,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Add bot response to chat
          addMessageToChat("bot", data.response)

          // Scroll to bottom of chat
          chatBox.scrollTop = chatBox.scrollHeight
        })
        .catch((error) => {
          console.error("Error:", error)
          addMessageToChat("bot", "Sorry, I encountered an error. Please try again.")
        })
    })

    // Function to add message to chat
    function addMessageToChat(sender, message) {
      const messageElement = document.createElement("div")
      messageElement.classList.add("chat-message")
      messageElement.classList.add(sender === "user" ? "user-message" : "bot-message")
      messageElement.textContent = message

      chatBox.appendChild(messageElement)
      chatBox.scrollTop = chatBox.scrollHeight
    }

    // Add initial bot message
    const tumorType = localStorage.getItem("tumorType") || "No tumor"
    addMessageToChat(
      "bot",
      `Hello! I'm your NeuroAssist chatbot. I can answer questions about ${tumorType} and provide general information about brain tumors. How can I help you today?`,
    )
  }
})
