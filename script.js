// Mobile menu toggle
document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("active")
    })

    // Close menu when clicking on a link
    document.querySelectorAll(".nav-menu a").forEach((link) => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("active")
      })
    })
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
})

// Update the signup form handler to send data to Python backend
document.addEventListener("DOMContentLoaded", () => {
  // Signup form
  const signupForm = document.getElementById("signupForm")
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault()

      if (validateForm("signupForm")) {
        // Show loading state
        const submitButton = signupForm.querySelector('button[type="submit"]')
        const originalText = submitButton.innerHTML
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...'
        submitButton.disabled = true

        try {
          // Get form data
          const formData = new FormData(signupForm)

          // Convert FormData to URLSearchParams for proper encoding
          const params = new URLSearchParams()
          for (const [key, value] of formData.entries()) {
            params.append(key, value)
          }

          // Send POST request to Python backend
          const response = await fetch("/signup", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: params.toString(),
          })

          const result = await response.json()

          if (result.success) {
            showNotification("Account created successfully! Welcome to FarmConnect!", "success")

            // Store user data for immediate login
            localStorage.setItem("currentUser", JSON.stringify(result.user))

            // Redirect to forum after short delay
            setTimeout(() => {
              window.location.href = "forum.html"
            }, 2000)
          } else {
            showNotification(result.message || "Failed to create account. Please try again.", "error")
          }
        } catch (error) {
          console.error("Signup error:", error)
          showNotification("Connection error. Please check your internet connection and try again.", "error")
        } finally {
          // Reset button state
          submitButton.innerHTML = originalText
          submitButton.disabled = false
        }
      }
    })
  }

  // Signin form (keep existing functionality)
  const signinForm = document.getElementById("signinForm")
  if (signinForm) {
    signinForm.addEventListener("submit", async (e) => {
      e.preventDefault()
      if (validateForm("signinForm")) {
        const submitButton = signinForm.querySelector('button[type="submit"]')
        const originalText = submitButton.innerHTML
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...'
        submitButton.disabled = true

        try {
          // Get form data
          const formData = new FormData(signinForm)
          const email = formData.get("email")
          const password = formData.get("password")

          // Send POST request to Python backend
          const response = await fetch("/signin", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
              email: email,
              password: password,
            }),
          })

          const result = await response.json()

          if (result.success) {
            // Store user data in localStorage for session management
            localStorage.setItem("currentUser", JSON.stringify(result.user))
            showNotification("Welcome back! Redirecting to dashboard...", "success")

            // Redirect to dashboard or forum
            setTimeout(() => {
              window.location.href = "forum.html"
            }, 1500)
          } else {
            showNotification(result.message, "error")
          }
        } catch (error) {
          console.error("Sign-in error:", error)
          showNotification("Connection error. Please try again.", "error")
        } finally {
          // Reset button state
          submitButton.innerHTML = originalText
          submitButton.disabled = false
        }
      }
    })
  }
})

// Enhanced form validation with better error messaging
function validateForm(formId) {
  const form = document.getElementById(formId)
  if (!form) return false

  const inputs = form.querySelectorAll("input[required], select[required], textarea[required]")
  let isValid = true
  let firstErrorField = null

  // Clear previous error states
  inputs.forEach((input) => {
    input.style.borderColor = "#e0e0e0"
    const errorMsg = input.parentNode.querySelector(".error-message")
    if (errorMsg) {
      errorMsg.remove()
    }
  })

  inputs.forEach((input) => {
    let fieldValid = true
    let errorMessage = ""

    if (!input.value.trim()) {
      fieldValid = false
      errorMessage = `${input.labels[0]?.textContent || "This field"} is required`
    } else {
      // Specific validation rules
      switch (input.type) {
        case "email":
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          if (!emailRegex.test(input.value)) {
            fieldValid = false
            errorMessage = "Please enter a valid email address"
          }
          break
        case "password":
          if (input.value.length < 6) {
            fieldValid = false
            errorMessage = "Password must be at least 6 characters long"
          }
          break
      }
    }

    if (!fieldValid) {
      input.style.borderColor = "#e74c3c"

      // Add error message
      const errorDiv = document.createElement("div")
      errorDiv.className = "error-message"
      errorDiv.style.cssText = "color: #e74c3c; font-size: 0.8rem; margin-top: 0.25rem;"
      errorDiv.textContent = errorMessage
      input.parentNode.appendChild(errorDiv)

      if (!firstErrorField) {
        firstErrorField = input
      }
      isValid = false
    }
  })

  // Password confirmation check for signup
  if (formId === "signupForm") {
    const password = document.getElementById("password")
    const confirmPassword = document.getElementById("confirmPassword")

    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.style.borderColor = "#e74c3c"

      const errorDiv = document.createElement("div")
      errorDiv.className = "error-message"
      errorDiv.style.cssText = "color: #e74c3c; font-size: 0.8rem; margin-top: 0.25rem;"
      errorDiv.textContent = "Passwords do not match"
      confirmPassword.parentNode.appendChild(errorDiv)

      isValid = false
      if (!firstErrorField) {
        firstErrorField = confirmPassword
      }
    }
  }

  // Focus on first error field
  if (firstErrorField) {
    firstErrorField.focus()
  }

  return isValid
}

// Forum functionality
function showNewPostForm() {
  const form = document.getElementById("newPostForm")
  if (form) {
    form.style.display = "block"
    form.scrollIntoView({ behavior: "smooth" })
  }
}

function hideNewPostForm() {
  const form = document.getElementById("newPostForm")
  if (form) {
    form.style.display = "none"
  }
}

function toggleLike(button) {
  const isLiked = button.classList.contains("liked")
  const countSpan = button.querySelector("span")
  let count = Number.parseInt(countSpan.textContent)

  if (isLiked) {
    button.classList.remove("liked")
    count--
  } else {
    button.classList.add("liked")
    count++
  }

  countSpan.textContent = count
}

// Search functionality (placeholder)
function searchPosts(query) {
  // This would typically send a request to your Python backend
  console.log("Searching for:", query)
}

// Enhanced notification system with different types
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification ${type}`

  // Set icon based on type
  let icon = "fas fa-info-circle"
  let bgColor = "var(--secondary-green)"

  switch (type) {
    case "success":
      icon = "fas fa-check-circle"
      bgColor = "#28a745"
      break
    case "error":
      icon = "fas fa-exclamation-circle"
      bgColor = "#dc3545"
      break
    case "warning":
      icon = "fas fa-exclamation-triangle"
      bgColor = "#ffc107"
      break
  }

  notification.innerHTML = `
    <i class="${icon}" style="margin-right: 0.5rem;"></i>
    ${message}
  `

  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 20px;
    background: ${bgColor};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 5px;
    box-shadow: var(--shadow);
    z-index: 1001;
    animation: slideIn 0.3s ease;
    max-width: 400px;
    word-wrap: break-word;
  `

  document.body.appendChild(notification)

  // Auto remove after 5 seconds
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease"
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove()
      }
    }, 300)
  }, 5000)

  // Click to dismiss
  notification.addEventListener("click", () => {
    notification.style.animation = "slideOut 0.3s ease"
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove()
      }
    }, 300)
  })
}

// Add CSS animation for notifications
const style = document.createElement("style")
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
  `

// Add slideOut animation
const existingStyle = document.querySelector("style")
if (existingStyle) {
  existingStyle.textContent += `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
  `
}
document.head.appendChild(style)

// Simulate real-time updates (placeholder)
function simulateRealTimeUpdates() {
  // This would typically use WebSockets or Server-Sent Events
  // to receive real-time updates from your Python backend
  setInterval(() => {
    // Simulate new post notification
    if (Math.random() > 0.95) {
      showNotification("New post in Crops & Planting category!")
    }
  }, 10000)
}

// Initialize real-time updates if on forum page
if (window.location.pathname.includes("forum.html")) {
  simulateRealTimeUpdates()
}

// Add function to check if user is logged in
function getCurrentUser() {
  const userData = localStorage.getItem("currentUser")
  return userData ? JSON.parse(userData) : null
}

// Add function to logout
function logout() {
  localStorage.removeItem("currentUser")
  window.location.href = "index.html"
}
