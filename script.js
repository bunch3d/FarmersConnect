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

// Form validation and submission
function validateForm(formId) {
  const form = document.getElementById(formId)
  if (!form) return false

  const inputs = form.querySelectorAll("input[required], select[required], textarea[required]")
  let isValid = true

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      input.style.borderColor = "#e74c3c"
      isValid = false
    } else {
      input.style.borderColor = "#e0e0e0"
    }
  })

  // Password confirmation check for signup
  if (formId === "signupForm") {
    const password = document.getElementById("password")
    const confirmPassword = document.getElementById("confirmPassword")

    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.style.borderColor = "#e74c3c"
      alert("Passwords do not match!")
      isValid = false
    }
  }

  return isValid
}

// Handle form submissions
document.addEventListener("DOMContentLoaded", () => {
  // Signup form
  const signupForm = document.getElementById("signupForm")
  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault()
      if (validateForm("signupForm")) {
        // Simulate form submission
        alert("Account created successfully! Please check your email for verification.")
        // In a real application, you would send this data to your Python backend
        console.log("Signup data:", new FormData(signupForm))
      }
    })
  }

  // Signin form
  const signinForm = document.getElementById("signinForm")
  if (signinForm) {
    signinForm.addEventListener("submit", (e) => {
      e.preventDefault()
      if (validateForm("signinForm")) {
        // Simulate form submission
        alert("Welcome back! Redirecting to dashboard...")
        // In a real application, you would authenticate with your Python backend
        console.log("Signin data:", new FormData(signinForm))
      }
    })
  }
})

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

// Notification system (placeholder)
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification ${type}`
  notification.textContent = message
  notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: var(--secondary-green);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: var(--shadow);
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `

  document.body.appendChild(notification)

  setTimeout(() => {
    notification.remove()
  }, 3000)
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
