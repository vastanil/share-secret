document.getElementById("secretForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const secret = document.getElementById("secret").value;
    const password = document.getElementById("password").value;
    const expiry = document.getElementById("expiry").value;

    const res = await fetch("http://backend:5000/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ secret, password, expiry })
    });

    const data = await res.json();

    const finalURL = `http://34.194.62.140:3000${data.url}`;
    document.getElementById("secretURL").textContent = finalURL;
    document.getElementById("secretURL").href = finalURL;

    document.getElementById("result").classList.remove("hidden");
});

