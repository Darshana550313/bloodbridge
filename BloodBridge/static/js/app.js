document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const hospitalFields = document.querySelector(".hospital-fields");

    if (roleSelect && hospitalFields) {
        const toggleHospitalFields = () => {
            hospitalFields.classList.toggle("d-none", roleSelect.value !== "hospital");
        };
        roleSelect.addEventListener("change", toggleHospitalFields);
        toggleHospitalFields();
    }

    document.querySelectorAll(".table-search").forEach((input) => {
        input.addEventListener("input", () => {
            const table = document.getElementById(input.dataset.table);
            if (!table) return;
            const query = input.value.toLowerCase();
            table.querySelectorAll("tbody tr").forEach((row) => {
                row.style.display = row.innerText.toLowerCase().includes(query) ? "" : "none";
            });
        });
    });
});

async function renderInventoryChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) return;

    const response = await fetch("/api/inventory");
    const data = await response.json();

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Units Available",
                data: data.units,
                backgroundColor: ["#d71920", "#ef5350", "#ff8a80", "#b71c1c", "#f44336", "#c62828", "#e57373", "#ff5252"],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });
}

