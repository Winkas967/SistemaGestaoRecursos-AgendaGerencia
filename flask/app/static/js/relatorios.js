const root = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");
const iconSun = document.getElementById("iconSun");
const iconMoon = document.getElementById("iconMoon");
const label = document.getElementById("themeLabel");

function applyTheme(theme) {
    root.setAttribute("data-theme", theme);

    if (theme === "dark") {
        iconSun.style.display = "none";
        iconMoon.style.display = "block";
        label.textContent = "Modo claro";
    } else {
        iconSun.style.display = "block";
        iconMoon.style.display = "none";
        label.textContent = "Modo escuro";
    }

    localStorage.setItem("theme", theme);
    atualizarCoresGraficos(theme);
}

let chartSetor = null;
let chartPeriodo = null;

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
let currentTheme = savedTheme || (prefersDark ? "dark" : "light");

applyTheme(currentTheme);

window.addEventListener("load", () => {
    root.classList.remove("is-loading");
    root.classList.add("is-ready");
});

toggleBtn.addEventListener("click", () => {
    currentTheme = currentTheme === "light" ? "dark" : "light";
    applyTheme(currentTheme);
});

const filtroForm = document.getElementById("form-filtros");

if (filtroForm) {
    filtroForm.addEventListener("submit", () => {
        const btn = filtroForm.querySelector(".btn-filtrar");
        if (btn && !btn.classList.contains("is-loading")) {
            btn.classList.add("is-loading");
        }
    });
}

/* ==========================================================
   Gráficos (Chart.js)
   Os dados abaixo vêm do backend via Jinja. Se a variável não
   existir, usamos um conjunto de exemplo para a tela nunca
   ficar quebrada durante o desenvolvimento.
   ========================================================== */

const PALETA_VERDE = ["#00995C", "#33ad7d", "#66c29e", "#99d6bf", "#0d5c3a"];
const COR_DESTAQUE = "#d9a544";




function corDoTema() {
    const styles = getComputedStyle(root);
    return {
        texto: styles.getPropertyValue("--text-muted").trim() || "#5f7568",
        grade: styles.getPropertyValue("--header-line").trim() || "#e1efe6",
    };
}

function montarGraficoSetor(dados) {
    const canvas = document.getElementById("graficoSetor");
    if (!canvas || typeof Chart === "undefined") return;

    const { texto, grade } = corDoTema();

    chartSetor = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: dados.labels,
            datasets: [{
                data: dados.valores,
                backgroundColor: dados.labels.map((_, i) => PALETA_VERDE[i % PALETA_VERDE.length]),
                borderWidth: 0,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.parsed} uso(s)`,
                    },
                },
            },
        },
    });

    montarLegendaSetor(dados.labels);
}

function montarLegendaSetor(labels) {
    const legenda = document.getElementById("legendaSetor");
    if (!legenda) return;

    legenda.innerHTML = "";
    labels.forEach((label, i) => {
        const li = document.createElement("li");
        const dot = document.createElement("span");
        dot.className = "legend-dot";
        dot.style.background = PALETA_VERDE[i % PALETA_VERDE.length];
        li.appendChild(dot);
        li.append(label);
        legenda.appendChild(li);
    });
}

function montarGraficoPeriodo(dados) {
    const canvas = document.getElementById("graficoPeriodo");
    if (!canvas || typeof Chart === "undefined") return;

    const { texto, grade } = corDoTema();

    chartPeriodo = new Chart(canvas, {
        type: "line",
        data: {
            labels: dados.labels,
            datasets: [{
                label: "Registros",
                data: dados.valores,
                borderColor: "#00995C",
                backgroundColor: "rgba(0, 153, 92, 0.14)",
                pointBackgroundColor: COR_DESTAQUE,
                pointBorderColor: "#ffffff",
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.35,
                fill: true,
                borderWidth: 2.5,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: texto }, grid: { display: false } },
                y: {
                    beginAtZero: true,
                    ticks: { color: texto, precision: 0 },
                    grid: { color: grade },
                },
            },
        },
    });
}

function atualizarCoresGraficos(theme) {
    if (!chartPeriodo) return;
    const { texto, grade } = corDoTema();
    chartPeriodo.options.scales.x.ticks.color = texto;
    chartPeriodo.options.scales.y.ticks.color = texto;
    chartPeriodo.options.scales.y.grid.color = grade;
    chartPeriodo.update();
}

function iniciarGraficos() {
    const dadosSetor = window.DADOS_SETOR || {
        labels: ["T.I.C", "Enfermagem", "Auditório", "RH", "Financeiro"],
        valores: [14, 9, 7, 4, 3],
    };

    const dadosPeriodo = window.DADOS_PERIODO || {
        labels: ["01/06", "08/06", "15/06", "22/06", "29/06"],
        valores: [3, 6, 4, 8, 5],
    };

    if (dadosSetor.labels.length) {
        montarGraficoSetor(dadosSetor);
    }
    if (dadosPeriodo.labels.length) {
        montarGraficoPeriodo(dadosPeriodo);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciarGraficos);
} else {
    iniciarGraficos();
}
