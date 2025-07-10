// Enhanced FarmConnect JavaScript with Connection Error Fixes
// This version includes better error handling and connection diagnostics

// Configuration
const CONFIG = {
  SERVER_URL: "http://localhost:8000",
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
}

// Connection status tracking
const connectionStatus = {
  isOnline: true,
  lastError: null,
  retryCount: 0,
}

// Enhanced fetch with retry logic and better error handling
async function enhancedFetch(url, options = {}) {
  const fullUrl = url.startsWith("http") ? url : `${CONFIG.SERVER_URL}${url}`

  // Default options
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    timeout: CONFIG.TIMEOUT,
  }

  const finalOptions = { ...defaultOptions, ...options }

  console.log(`🌐 Making request to: ${fullUrl}`)
  console.log(`📋 Options:`, finalOptions)

  for (let attempt = 1; attempt <= CONFIG.RETRY_ATTEMPTS; attempt++) {
    try {
      console.log(`🔄 Attempt ${attempt}/${CONFIG.RETRY_ATTEMPTS}`)

      // Create AbortController for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT)

      const response = await fetch(fullUrl, {
        ...finalOptions,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      console.log(`📡 Response status: ${response.status}`)
      console.log(`📡 Response headers:`, Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get("content-type")
      let data

      if (contentType && contentType.includes("application/json")) {
        data = await response.json()
      } else {
        data = await response.text()
      }

      console.log(`✅ Response data:`, data)

      // Reset connection status on success
      connectionStatus.isOnline = true
      connectionStatus.lastError = null
      connectionStatus.retryCount = 0

      return { success: true, data, response }
    } catch (error) {
      console.error(`❌ Attempt ${attempt} failed:`, error)

      connectionStatus.lastError = error
      connectionStatus.retryCount = attempt

      // Check error type
      if (error.name === "AbortError") {
        console.error("⏰ Request timed out")
      } else if (error.message.includes("Failed to fetch")) {
        console.error("🔌 Network connection failed - server might be down")
        connectionStatus.isOnline = false
      } else if (error.message.includes("CORS")) {
        console.error("🚫 CORS error - server not allowing requests")
      }

      // If this is the last attempt, throw the error
      if (attempt === CONFIG.RETRY_ATTEMPTS) {
        throw error
      }

      // Wait before retrying
      console.log(`⏳ Waiting ${CONFIG.RETRY_DELAY}ms before retry...`)
      await new Promise((resolve) => setTimeout(resolve, CONFIG.RETRY_DELAY))
    }
  }
}

// Connection diagnostics
async function runConnectionDiagnostics() {
  console.log("🔍 Running connection diagnostics...")

  const diagnostics = {
    timestamp: new Date().toISOString(),
    serverUrl: CONFIG.SERVER_URL,
    userAgent: navigator.userAgent,
    online: navigator.onLine,
    tests: {},
  }

  // Test 1: Basic connectivity
  try {
    console.log("🧪 Test 1: Basic server connectivity")
    const response = await fetch(`${CONFIG.SERVER_URL}/debug/db-info`, {
      method: "GET",
      mode: "cors",
    })
    diagnostics.tests.basicConnectivity = {
      success: true,
      status: response.status,
      statusText: response.statusText,
    }
    console.log("✅ Basic connectivity: PASS")
  } catch (error) {
    diagnostics.tests.basicConnectivity = {
      success: false,
      error: error.message,
    }
    console.log("❌ Basic connectivity: FAIL -", error.message)
  }

  // Test 2: CORS headers
  try {
    console.log("🧪 Test 2: CORS headers")
    const response = await fetch(`${CONFIG.SERVER_URL}/debug/db-info`, {
      method: "OPTIONS",
    })
    diagnostics.tests.corsHeaders = {
      success: true,
      headers: Object.fromEntries(response.headers.entries()),
    }
    console.log("✅ CORS headers: PASS")
  } catch (error) {
    diagnostics.tests.corsHeaders = {
      success: false,
      error: error.message,
    }
    console.log("❌ CORS headers: FAIL -", error.message)
  }

  // Test 3: POST request capability
  try {
    console.log("🧪 Test 3: POST request capability")
    const response = await fetch(`${CONFIG.SERVER_URL}/debug/test-db`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "test=1",
    })
    const data = await response.json()
    diagnostics.tests.postRequest = {
      success: true,
      data: data,
    }
    console.log("✅ POST request: PASS")
  } catch (error) {
    diagnostics.tests.postRequest = {
      success: false,
      error: error.message,
    }
    console.log("❌ POST request: FAIL -", error.message)
  }

  console.log("📊 Diagnostics complete:", diagnostics)
  return diagnostics
}

// Enhanced form submission with better error handling
async function submitFormWithRetry(formData, endpoint) {
  console.log(`📝 Submitting form to ${endpoint}`)
  console.log("📋 Form data:", Object.fromEntries(formData.entries()))

  try {
    const result = await enhancedFetch(endpoint, {
      method: "POST",
      body: formData,
    })

    return result.data
  } catch (error) {
    console.error("💥 Form submission failed:", error)

    // Provide user-friendly error messages
    let userMessage = "An error occurred. Please try again."

    if (error.message.includes("Failed to fetch")) {
      userMessage = "Cannot connect to server. Please check if the server is running and try again."
    } else if (error.message.includes("timeout")) {
      userMessage = "Request timed out. Please check your connection and try again."
    } else if (error.message.includes("404")) {
      userMessage = "Server endpoint not found. Please contact support."
    } else if (error.message.includes("500")) {
      userMessage = "Server error occurred. Please try again later."
    }

    return {
      success: false,
      error: error.message,
      userMessage: userMessage,
      diagnostics: await runConnectionDiagnostics(),
    }
  }
}

// Mobile menu toggle (existing functionality)
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 FarmConnect JavaScript loaded")
  console.log("⚙️ Configuration:", CONFIG)

  // Check initial connection status
  if (!navigator.onLine) {
    console.warn("⚠️ Browser is offline")
    showNotification("You appear to be offline. Some features may not work.", "warning")
  }

  // Mobile menu functionality
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("active")
    })

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

  // Run initial diagnostics if on signup/signin page
  if (window.location.pathname.includes("signup.html") || window.location.pathname.includes("signin.html")) {
    console.log("🔍 Running initial connection diagnostics...")
    runConnectionDiagnostics()
  }
})

// Enhanced signup form handler
document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signupForm")
  if (signupForm) {
    console.log("📝 Signup form found, attaching handler")

    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault()
      console.log("📤 Signup form submitted")

      if (validateForm("signupForm")) {
        const submitButton = signupForm.querySelector('button[type="submit"]')
        const originalText = submitButton.innerHTML

        // Show loading state
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...'
        submitButton.disabled = true

        try {
          // Get form data
          const formData = new FormData(signupForm)

          // Log form data for debugging
          console.log("📋 Signup form data:")
          for (const [key, value] of formData.entries()) {
            if (key === "password" || key === "confirmPassword") {
              console.log(`  ${key}: ${"*".repeat(value.length)}`)
            } else {
              console.log(`  ${key}: ${value}`)
            }
          }

          // Submit form
          const result = await submitFormWithRetry(formData, "/signup")

          if (result.success) {
            console.log("✅ Signup successful:", result)
            showNotification("Account created successfully! Welcome to FarmConnect!", "success")

            // Store user data
            if (result.user) {
              localStorage.setItem("currentUser", JSON.stringify(result.user))
            }

            // Redirect after delay
            setTimeout(() => {
              window.location.href = "forum.html"
            }, 2000)
          } else {
            console.error("❌ Signup failed:", result)

            let errorMessage = result.userMessage || result.message || "Failed to create account. Please try again."

            // Show detailed error for debugging
            if (result.debug_info) {
              console.error("🔍 Debug info:", result.debug_info)

              // Add debug info to error message in development
              if (window.location.hostname === "localhost") {
                errorMessage += `\n\nDebug: ${result.debug_info.step} - ${result.debug_info.error || "Unknown error"}`
              }
            }

            showNotification(errorMessage, "error")

            // Show diagnostics if available
            if (result.diagnostics) {
              console.log("🔍 Connection diagnostics:", result.diagnostics)
            }
          }
        } catch (error) {
          console.error("💥 Unexpected signup error:", error)
          showNotification("An unexpected error occurred. Please check the console for details.", "error")
        } finally {
          // Reset button state
          submitButton.innerHTML = originalText
          submitButton.disabled = false
        }
      }
    })
  }

  // Enhanced signin form handler
  const signinForm = document.getElementById("signinForm")
  if (signinForm) {
    console.log("🔐 Signin form found, attaching handler")

    signinForm.addEventListener("submit", async (e) => {
      e.preventDefault()
      console.log("📤 Signin form submitted")

      if (validateForm("signinForm")) {
        const submitButton = signinForm.querySelector('button[type="submit"]')
        const originalText = submitButton.innerHTML

        // Show loading state
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...'
        submitButton.disabled = true

        try {
          // Get form data
          const formData = new FormData(signinForm)

          console.log("📋 Signin attempt for:", formData.get("email"))

          // Submit form
          const result = await submitFormWithRetry(formData, "/signin")

          if (result.success) {
            console.log("✅ Signin successful:", result)

            // Store user data
            if (result.user) {
              localStorage.setItem("currentUser", JSON.stringify(result.user))
            }

            showNotification("Welcome back! Redirecting to dashboard...", "success")

            // Redirect after delay
            setTimeout(() => {
              window.location.href = "forum.html"
            }, 1500)
          } else {
            console.error("❌ Signin failed:", result)
            showNotification(result.userMessage || result.message || "Invalid email or password", "error")
          }
        } catch (error) {
          console.error("💥 Unexpected signin error:", error)
          showNotification("An unexpected error occurred. Please check the console for details.", "error")
        } finally {
          // Reset button state
          submitButton.innerHTML = originalText
          submitButton.disabled = false
        }
      }
    })
  }
})

// Enhanced form validation
function validateForm(formId) {
  console.log(`🔍 Validating form: ${formId}`)

  const form = document.getElementById(formId)
  if (!form) {
    console.error(`❌ Form ${formId} not found`)
    return false
  }

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

  console.log(`✅ Form validation result: ${isValid}`)
  return isValid
}

// Enhanced notification system
function showNotification(message, type = "info") {
  console.log(`📢 Notification (${type}): ${message}`)

  const notification = document.createElement("div")
  notification.className = `notification ${type}`

  // Set icon and color based on type
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
        white-space: pre-line;
    `

  document.body.appendChild(notification)

  // Auto remove after 8 seconds (longer for error messages)
  const duration = type === "error" ? 8000 : 5000
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease"
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove()
      }
    }, 300)
  }, duration)

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

// Connection status monitoring
window.addEventListener("online", () => {
  console.log("🌐 Connection restored")
  connectionStatus.isOnline = true
  showNotification("Connection restored!", "success")
})

window.addEventListener("offline", () => {
  console.log("📵 Connection lost")
  connectionStatus.isOnline = false
  showNotification("Connection lost. Please check your internet connection.", "warning")
})

// Debug functions for console
window.farmConnectDebug = {
  runDiagnostics: runConnectionDiagnostics,
  checkConnection: () => connectionStatus,
  testServer: async () => {
    try {
      const result = await enhancedFetch("/debug/db-info")
      console.log("Server test result:", result)
      return result
    } catch (error) {
      console.error("Server test failed:", error)
      return { success: false, error: error.message }
    }
  },
  config: CONFIG,
}

// Forum functionality (existing)
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

// Utility functions
function getCurrentUser() {
  const userData = localStorage.getItem("currentUser")
  return userData ? JSON.parse(userData) : null
}

function logout() {
  localStorage.removeItem("currentUser")
  window.location.href = "index.html"
}

// Add CSS animations
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
document.head.appendChild(style)

console.log("✅ FarmConnect JavaScript fully loaded with enhanced error handling")
