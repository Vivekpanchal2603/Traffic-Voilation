let allViolations = [];


async function loadViolations() {
    try {
        const res = await fetch("/violations");
        const data = await res.json();

        allViolations = data.data || [];

        const searchValue =
            document.getElementById("searchPlate")?.value?.toLowerCase() || "";

        if (searchValue) {
            filterViolations();
        } else {
            renderViolations(allViolations);
        }

        updateStats();

    } catch (error) {
        console.error("Failed to load violations:", error);
    }
}


function renderViolations(records) {
    const tbody = document.querySelector("#violationTable tbody");
    tbody.innerHTML = "";

    records.forEach(v => {
        tbody.innerHTML += `
            <tr>
                <td>${v.violation_id}</td>
                <td>${v.timestamp}</td>
                <td>${v.number_plate}</td>
                <td>${v.helmet_violation}</td>
                <td>${v.triple_seat_violation}</td>
                <td>${v.phone_violation}</td>
                <td>₹${v.fine_amount}</td>
                <td>
                    <button onclick="markPaid('${v.violation_id}')">
                        Paid ✓
                    </button>
                </td>
            </tr>
        `;
    });
}


function updateStats() {
    document.getElementById("totalViolations").innerText =
        allViolations.length;

    const revenue = allViolations.reduce(
        (sum, v) => sum + Number(v.fine_amount),
        0
    );

    document.getElementById("totalRevenue").innerText =
        `₹${revenue}`;
}


function filterViolations() {
    const search = document
        .getElementById("searchPlate")
        .value
        .toLowerCase();

    const filtered = allViolations.filter(v =>
        v.number_plate.toLowerCase().includes(search)
    );

    renderViolations(filtered);
}


async function markPaid(violationId) {
    const confirmed = confirm(
        "Are you sure this fine has been paid?\nThis record will be removed."
    );

    if (!confirmed) return;

    await fetch("/violations/pay", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            violation_id: violationId
        })
    });

    loadViolations();
}


/* INITIAL LOAD */
loadViolations();


/* REAL-TIME AUTO REFRESH EVERY 5 SECONDS */
setInterval(loadViolations, 5000);