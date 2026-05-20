function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  const target = document.getElementById(pageId);
  if (target) {
    target.classList.remove('hidden');
  }

  if (pageId === 'adminScanner') {
    startQRScanner();
  } else {
    stopQRScannerEngineOnly();
  }
}

//Uppercase transformation for all inputs except email and password fields
document.addEventListener("input", function(e) {
  if (
    e.target.type !== "email" &&
    e.target.id !== "registerEmail" &&
    e.target.id !== "studentEmail" &&
    e.target.id !== "adminEmail" && 
    e.target.id !== "studentPassword" &&
    e.target.id !== "adminPassword" &&
    e.target.id !== "registerPassword" &&
    e.target.id !== "registerConfirmPassword" &&
    e.target.id !== "password" &&
    e.target.id !== "confirmPassword"
  ) {
    e.target.value = e.target.value.toUpperCase();
  }
});

async function studentLogin() {
    const email = document.querySelector("#studentEmail").value;
    const password = document.querySelector("#studentPassword").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    if (!email.endsWith("@rtu.edu.ph")) {
        alert("Only RTU institutional email allowed.");
        return;
    }

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
    const email = document.querySelector("#adminEmail").value;
    const password = document.querySelector("#adminPassword").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    if (!email.endsWith("@rtu.edu.ph")) {
        alert("Only RTU institutional email allowed.");
        return;
    }

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
        alert(data.detail || "Login failed");
    }
}

async function registerUser() {
    const role = document.querySelector('input[name="roleStudent"]:checked')?.value
                || document.querySelector('input[name="roleAdmin"]:checked')?.value;

    const name = document.getElementById("studentRegisterName")?.value 
                || document.getElementById("adminRegisterName")?.value;

    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById("registerConfirmPassword").value;

    if (!email.endsWith("@rtu.edu.ph")) {
        alert("Only RTU institutional email allowed.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    if (!name || !name.trim()) {
        alert("Name is required.");
        return;
    }

    const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, email, password, role })
    });

    if (res.ok) { 
        alert("Account created successfully! You will be directed to the login page.");
        resetPage("accountCreationStep2");
        resetPage("accountCreationForStudent");
        resetPage("accountCreationForAdmin");
        resetPage("studentLogin");
        resetPage("adminLogin");
        showPage("start");
    } else {
        const data = await res.json();
        alert(data.detail || "Registration failed");
    }
}

function validateStep1() {
    const role = document.querySelector('input[name="roleStudent"]:checked')?.value
                || document.querySelector('input[name="roleAdmin"]:checked')?.value;
    
    const name = document.getElementById("studentRegisterName")?.value 
                || document.getElementById("adminRegisterName")?.value;
    
    if(!role) {
        return alert("Please select a role.");
    }

    if(!name?.trim()) {
        return alert("Name is required.");  
    }

    if(role === "roleStudent" || role === "student") {
        const studentNumber = document.getElementById("studentNumber")?.value;
        const yearLevel = document.getElementById("yearLevel")?.value;
        const department = document.getElementById("department")?.value;
        const course = document.getElementById("course")?.value;

        if (!studentNumber?.trim() || !yearLevel?.trim() || !department?.trim() || !course?.trim()) {
            alert("Please complete all information.");
            return;
        }
    }

    if (role === "roleAdmin" || role === "admin") {
        const adminStudentNumber = document.getElementById("adminStudentNumber")?.value;
        const adminYearLevel = document.getElementById("adminYearLevel")?.value;
        const organization = document.getElementById("organization")?.value;
        const position = document.getElementById("position")?.value;

        if (!adminStudentNumber?.trim() || !adminYearLevel?.trim() || !organization?.trim() || !position?.trim()) {
            alert("Please complete all information");
            return;
        }
    }

    showPage("accountCreationStep2");
}

let html5QrcodeScanner = null;

function onScanSuccess(decodedText, decodedResult) {
    document.getElementById('qr-reader-results').innerText = `Scanned ID/Data: ${decodedText}`;
    alert(`Attendance logged successfully for: ${decodedText}`);
    stopScannerAndGoBack();
}

function startQRScanner() {
    if (!html5QrcodeScanner) {
        html5QrcodeScanner = new Html5QrcodeScanner(
            "qr-reader", 
            { 
                fps: 15, 
                qrbox: { width: 250, height: 250 },
                supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA] 
            }, 
            false
        );
        html5QrcodeScanner.render(onScanSuccess, (error) => {});
    }
}

function stopQRScannerEngineOnly() {
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear().then(() => {
            html5QrcodeScanner = null;
            if (document.getElementById('qr-reader-results')) {
                document.getElementById('qr-reader-results').innerText = "";
            }
        }).catch(err => {
            console.error(err);
        });
    }
}

function stopScannerAndGoBack() {
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear().then(() => {
            html5QrcodeScanner = null;
            document.getElementById('qr-reader-results').innerText = "";
            showPage('adminHome');
        }).catch(err => {
            showPage('adminHome');
        });
    } else {
        showPage('adminHome');
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const toggleButtons = document.querySelectorAll(".toggle-password-btn");

    toggleButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            const targetId = this.getAttribute("data-target");
            const targetInput = document.getElementById(targetId);

            if (targetInput) {
                const isHidden = targetInput.getAttribute("type") === "password";
                targetInput.setAttribute("type", isHidden ? "text" : "password");
                this.style.opacity = isHidden ? "0.4" : "1.0";
            }
        });
    });
});