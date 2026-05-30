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

    document.querySelectorAll(".feature-card, .panel, .auth-card, .metric-card, .dashboard-heading, .alert, tbody tr").forEach((element) => {
        element.classList.add("reveal-on-scroll");
    });

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.14 });

    document.querySelectorAll(".reveal-on-scroll").forEach((element) => revealObserver.observe(element));

    initBloodBridgeScene();
    initAmbientMedicalScene();
});

function initBloodBridgeScene() {
    const canvas = document.getElementById("bloodBridge3d");
    if (!canvas || !window.THREE) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(0, 0.8, 8.4);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.7);
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.3);
    keyLight.position.set(4, 5, 6);
    const rimLight = new THREE.PointLight(0xb7eadb, 3.4, 16);
    rimLight.position.set(-4, -1, 4);
    scene.add(ambientLight, keyLight, rimLight);

    const group = new THREE.Group();
    scene.add(group);

    const redMaterial = new THREE.MeshStandardMaterial({
        color: 0xc73a4b,
        roughness: 0.38,
        metalness: 0.08,
        emissive: 0x3d0710,
        emissiveIntensity: 0.18
    });
    const coralMaterial = new THREE.MeshStandardMaterial({
        color: 0xf27f62,
        roughness: 0.42,
        metalness: 0.04
    });
    const mintMaterial = new THREE.MeshStandardMaterial({
        color: 0xb7eadb,
        roughness: 0.32,
        metalness: 0.16,
        transparent: true,
        opacity: 0.78
    });
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0xb7eadb, transparent: true, opacity: 0.34 });

    const cellGeometry = new THREE.TorusGeometry(0.36, 0.12, 18, 48);
    const coreGeometry = new THREE.SphereGeometry(0.19, 24, 16);
    const connectorPoints = [];

    for (let index = 0; index < 24; index += 1) {
        const cell = new THREE.Group();
        const ring = new THREE.Mesh(cellGeometry, index % 4 === 0 ? coralMaterial : redMaterial);
        const core = new THREE.Mesh(coreGeometry, redMaterial);
        core.scale.set(1.65, 1.65, 0.24);
        cell.add(ring, core);

        const angle = index * 0.74;
        const radius = 2.05 + (index % 5) * 0.32;
        cell.position.set(
            Math.cos(angle) * radius + 2.2,
            Math.sin(angle * 1.18) * 1.75,
            Math.sin(angle) * 1.2
        );
        cell.rotation.set(angle * 0.23, angle, angle * 0.38);
        cell.scale.setScalar(0.82 + (index % 4) * 0.08);
        cell.userData = { speed: 0.004 + index * 0.00018, offset: angle };
        group.add(cell);

        if (index % 3 === 0) {
            connectorPoints.push(cell.position.clone());
        }
    }

    for (let index = 0; index < connectorPoints.length - 1; index += 1) {
        const geometry = new THREE.BufferGeometry().setFromPoints([connectorPoints[index], connectorPoints[index + 1]]);
        group.add(new THREE.Line(geometry, lineMaterial));
    }

    const beadGeometry = new THREE.SphereGeometry(0.08, 18, 12);
    const helix = new THREE.Group();
    for (let index = 0; index < 36; index += 1) {
        const bead = new THREE.Mesh(beadGeometry, mintMaterial);
        const angle = index * 0.46;
        bead.position.set(
            Math.cos(angle) * 0.82 - 2.7,
            (index - 18) * 0.075,
            Math.sin(angle) * 0.82
        );
        helix.add(bead);
    }
    group.add(helix);

    let scrollProgress = 0;
    const updateScroll = () => {
        const maxScroll = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
        scrollProgress = window.scrollY / maxScroll;
    };

    const resize = () => {
        const rect = canvas.parentElement.getBoundingClientRect();
        renderer.setSize(rect.width, rect.height, false);
        camera.aspect = rect.width / Math.max(rect.height, 1);
        camera.updateProjectionMatrix();
    };

    window.addEventListener("resize", resize);
    window.addEventListener("scroll", updateScroll, { passive: true });
    resize();
    updateScroll();

    const clock = new THREE.Clock();
    const animate = () => {
        const elapsed = clock.getElapsedTime();
        group.rotation.y = elapsed * 0.07 + scrollProgress * 1.2;
        group.rotation.x = Math.sin(elapsed * 0.35) * 0.08 - scrollProgress * 0.28;
        group.position.y = -scrollProgress * 1.1;
        helix.rotation.y = elapsed * 0.85;

        group.children.forEach((child) => {
            if (!child.userData || child.userData.speed === undefined) return;
            child.rotation.x += child.userData.speed;
            child.rotation.y += child.userData.speed * 1.8;
            child.position.y += Math.sin(elapsed + child.userData.offset) * 0.0028;
        });

        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    };

    animate();
}

function initAmbientMedicalScene() {
    const canvas = document.getElementById("ambient3d");
    if (!canvas || !window.THREE) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 100);
    camera.position.set(0, 0, 9);

    scene.add(new THREE.AmbientLight(0xffffff, 1.4));
    const light = new THREE.DirectionalLight(0xffffff, 1.8);
    light.position.set(3, 4, 6);
    scene.add(light);

    const group = new THREE.Group();
    scene.add(group);

    const redMaterial = new THREE.MeshStandardMaterial({
        color: 0xc73a4b,
        roughness: 0.46,
        metalness: 0.05,
        transparent: true,
        opacity: 0.9
    });
    const tealMaterial = new THREE.MeshStandardMaterial({
        color: 0x0f766e,
        roughness: 0.36,
        metalness: 0.12,
        transparent: true,
        opacity: 0.74
    });
    const coralMaterial = new THREE.MeshStandardMaterial({
        color: 0xf27f62,
        roughness: 0.44,
        metalness: 0.05,
        transparent: true,
        opacity: 0.72
    });

    const torusGeometry = new THREE.TorusGeometry(0.22, 0.07, 16, 36);
    const sphereGeometry = new THREE.SphereGeometry(0.09, 18, 12);
    const plusBarGeometry = new THREE.BoxGeometry(0.32, 0.08, 0.08);

    for (let index = 0; index < 34; index += 1) {
        const object = new THREE.Group();
        const angle = index * 0.88;
        const row = index % 6;
        object.position.set(
            Math.cos(angle) * (3.2 + row * 0.34),
            Math.sin(angle * 0.72) * 2.9,
            -1.8 - (index % 5) * 0.55
        );
        object.userData = {
            baseY: object.position.y,
            drift: 0.5 + index * 0.04,
            speed: 0.004 + index * 0.00012
        };

        if (index % 5 === 0) {
            const horizontal = new THREE.Mesh(plusBarGeometry, tealMaterial);
            const vertical = new THREE.Mesh(plusBarGeometry, tealMaterial);
            vertical.rotation.z = Math.PI / 2;
            object.add(horizontal, vertical);
        } else if (index % 3 === 0) {
            object.add(new THREE.Mesh(sphereGeometry, coralMaterial));
        } else {
            object.add(new THREE.Mesh(torusGeometry, redMaterial));
        }

        object.rotation.set(angle * 0.2, angle * 0.4, angle * 0.1);
        group.add(object);
    }

    let scrollProgress = 0;
    const updateScroll = () => {
        const maxScroll = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
        scrollProgress = window.scrollY / maxScroll;
    };

    const resize = () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        renderer.setSize(width, height, false);
        camera.aspect = width / Math.max(height, 1);
        camera.updateProjectionMatrix();
    };

    window.addEventListener("resize", resize);
    window.addEventListener("scroll", updateScroll, { passive: true });
    resize();
    updateScroll();

    const clock = new THREE.Clock();
    const animate = () => {
        const elapsed = clock.getElapsedTime();
        group.rotation.y = elapsed * 0.035 + scrollProgress * 0.8;
        group.rotation.x = Math.sin(elapsed * 0.28) * 0.07;

        group.children.forEach((object) => {
            object.rotation.x += object.userData.speed;
            object.rotation.y += object.userData.speed * 1.45;
            object.position.y = object.userData.baseY + Math.sin(elapsed * object.userData.drift) * 0.12;
        });

        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    };

    animate();
}

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
                backgroundColor: ["#0f766e", "#c73a4b", "#f27f62", "#932637", "#5fb7a8", "#df6372", "#f6a78f", "#284553"],
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
