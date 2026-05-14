function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  const target = document.getElementById(pageId);
  if (target) {
    target.classList.remove('hidden');
  }
}

async function studentLogin() {
    const email = document.querySelector("#studentLogin input[type='email']").value;
    const password = document.querySelector("#studentLogin input[type='password']").value;

    const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    const data = await response.json();

    if (response.ok) {
        alert("Login successful!");

        // store token
        localStorage.setItem("token", data.access_token);

        showPage('studentHome');
    } else {
        alert(data.detail || "Login failed");
    }
}

async function studentLogin() {
    const email = document.querySelector("#studentLogin input[type='email']").value;
    const password = document.querySelector("#studentLogin input[type='password']").value;

    const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful!");
        showPage("studentHome");
    } else {
        alert(data.detail || "Login failed");
    }
}

async function adminLogin() {
    const email = document.querySelector("#adminLogin input[type='email']").value;
    const password = document.querySelector("#adminLogin input[type='password']").value;

    const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful!");
        showPage("adminHome");
    } else {
        alert("Login failed");
    }
} 

async function registerUser() {

    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    // Email Validation, only RTU institurional email allowed
    if (!email.endsWith("@rtu.edu.ph")) {
        alert("Only institutional email allowed (@rtu.edu.ph)");
        return;
    }

    const role = document.querySelector('input[name="role"]:checked')
        .parentElement.textContent
        .trim()
        .toLowerCase();

    const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            email,
            password,
            role
        })
    });

    const data = await response.json();

    if (response.ok) {
        alert("Account created successfully!");
        showPage("start"); // go back to login
    } else {
        alert(data.detail || "Registration failed");
    }
}