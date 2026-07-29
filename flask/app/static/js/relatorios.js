const root = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");
const iconSun = document.getElementById("iconSun");
const iconMoon = document.getElementById("iconMoon");
const label = document.getElementById("themeLabel");
const charts = [];

function corDoTema() {
    const styles = getComputedStyle(root);
    return {
        texto: styles.getPropertyValue("--text-muted").trim() || "#5f7568",
        grade: styles.getPropertyValue("--header-line").trim() || "#e1efe6",
    };
}

function atualizarCoresGraficos() {
    const { texto, grade } = corDoTema();

    charts.forEach((chart) => {
        if (chart.options.scales?.x?.ticks) chart.options.scales.x.ticks.color = texto;
        if (chart.options.scales?.y?.ticks) chart.options.scales.y.ticks.color = texto;
        if (chart.options.scales?.y?.grid) chart.options.scales.y.grid.color = grade;
        chart.update();
    });
}

function applyTheme(theme) {
    root.setAttribute("data-theme", theme);

    if (theme === "dark") {
        if (iconSun) iconSun.style.display = "none";
        if (iconMoon) iconMoon.style.display = "block";
        if (label) label.textContent = "Modo claro";
    } else {
        if (iconSun) iconSun.style.display = "block";
        if (iconMoon) iconMoon.style.display = "none";
        if (label) label.textContent = "Modo escuro";
    }

    localStorage.setItem("theme", theme);
    atualizarCoresGraficos();
}

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
let currentTheme = savedTheme || (prefersDark ? "dark" : "light");

applyTheme(currentTheme);

window.addEventListener("load", () => {
    root.classList.remove("is-loading");
    root.classList.add("is-ready");
});

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        applyTheme(currentTheme);
    });
}

const filtroForm = document.getElementById("form-filtros");

if (filtroForm) {
    filtroForm.addEventListener("submit", () => {
        const btn = filtroForm.querySelector(".btn-filtrar");
        if (btn && !btn.classList.contains("is-loading")) {
            btn.classList.add("is-loading");
        }
    });
}

function hashTexto(texto) {
    return [...texto].reduce((acc, char) => {
        return (acc * 31 + char.charCodeAt(0)) >>> 0;
    }, 7);
}

function criarAvatar(nome) {
    const hash = hashTexto(nome || "usuario");
    const peles = ["#f2c7a5", "#d89b73", "#b8734f", "#8f5d43", "#f0b98f"];
    const cabelos = ["#2c221f", "#5a3825", "#1f2933", "#7a4a24", "#111827"];
    const roupas = ["#00995c", "#2563eb", "#c2410c", "#7c3aed", "#0f766e"];
    const fundos = ["#dff4ea", "#e0f2fe", "#fef3c7", "#ede9fe", "#dcfce7", "#ffe4e6", "#fce7f3", "#ccfbf1"];

    const pele = peles[hash % peles.length];
    const cabelo = cabelos[(hash >> 3) % cabelos.length];
    const roupa = roupas[(hash >> 6) % roupas.length];
    const fundo = fundos[(hash >> 9) % fundos.length];
    const sorriso = hash % 2 === 0
        ? '<path d="M23 35c3 3 9 3 12 0" fill="none" stroke="#553226" stroke-width="2" stroke-linecap="round"/>'
        : '<path d="M24 35c2 2 8 2 10 0" fill="none" stroke="#553226" stroke-width="2" stroke-linecap="round"/>';
    const cabeloForma = hash % 3 === 0
        ? `<path d="M15 25c2-12 24-14 30 0-5-7-22-6-30 0z" fill="${cabelo}"/>`
        : hash % 3 === 1
            ? `<path d="M14 27c1-15 27-15 31 0-8-4-22-5-31 0z" fill="${cabelo}"/>`
            : `<path d="M16 21c8-10 24-6 28 6-10-5-19-6-28-6z" fill="${cabelo}"/>`;

    return `
        <svg viewBox="0 0 60 60" role="img" aria-label="Avatar do usuario">
            <rect width="60" height="60" rx="30" fill="${fundo}"/>
            <circle cx="30" cy="30" r="28" fill="none" stroke="#ffffff" stroke-width="3"/>
            <path d="M14 58c2-13 30-13 32 0z" fill="${roupa}"/>
            <circle cx="30" cy="29" r="15" fill="${pele}"/>
            ${cabeloForma}
            <circle cx="24" cy="30" r="1.8" fill="#2b211f"/>
            <circle cx="36" cy="30" r="1.8" fill="#2b211f"/>
            ${sorriso}
        </svg>
    `;
}

const userPanel = document.querySelector(".user-panel");
const userAvatar = document.querySelector(".user-avatar");

if (userPanel && userAvatar) {
    userAvatar.innerHTML = criarAvatar(userPanel.dataset.username);
}

const PALETA = ["#00995C", "#33ad7d", "#d9a544", "#2563eb", "#7c3aed", "#e0574a", "#0f766e", "#64748b"];

function dadosValidos(dados) {
    return dados
        && Array.isArray(dados.labels)
        && Array.isArray(dados.valores)
        && dados.labels.length > 0
        && dados.valores.length === dados.labels.length;
}

function mostrarEstadoGrafico(canvasId, mensagem) {
    const canvas = document.getElementById(canvasId);
    const container = canvas?.parentElement;
    if (!canvas || !container) return;

    canvas.hidden = true;
    const aviso = document.createElement("div");
    aviso.className = "chart-empty";
    aviso.setAttribute("role", "status");
    aviso.textContent = mensagem;
    container.appendChild(aviso);
}

function podeCriarGrafico(canvasId, dados) {
    if (typeof window.Chart === "undefined") {
        mostrarEstadoGrafico(canvasId, "Não foi possível carregar o gráfico.");
        return false;
    }

    if (!dadosValidos(dados)) {
        mostrarEstadoGrafico(canvasId, "Não há dados para este gráfico.");
        return false;
    }

    return Boolean(document.getElementById(canvasId));
}

function registrarGrafico(chart) {
    charts.push(chart);
    return chart;
}

function criarGraficoLinha(canvasId, dados, labelGrafico) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !podeCriarGrafico(canvasId, dados)) return;

    const { texto, grade } = corDoTema();

    registrarGrafico(new Chart(canvas, {
        type: "line",
        data: {
            labels: dados.labels,
            datasets: [{
                label: labelGrafico,
                data: dados.valores,
                borderColor: "#00995C",
                backgroundColor: "rgba(0, 153, 92, 0.14)",
                pointBackgroundColor: "#d9a544",
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
                y: { beginAtZero: true, ticks: { color: texto, precision: 0 }, grid: { color: grade } },
            },
        },
    }));
}

function criarGraficoBarras(canvasId, dados, labelGrafico) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !podeCriarGrafico(canvasId, dados)) return;

    const { texto, grade } = corDoTema();

    registrarGrafico(new Chart(canvas, {
        type: "bar",
        data: {
            labels: dados.labels,
            datasets: [{
                label: labelGrafico,
                data: dados.valores,
                backgroundColor: dados.labels.map((_, i) => PALETA[i % PALETA.length]),
                borderRadius: 8,
                maxBarThickness: 44,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: texto }, grid: { display: false } },
                y: { beginAtZero: true, ticks: { color: texto, precision: 0 }, grid: { color: grade } },
            },
        },
    }));
}

function criarGraficoRosca(canvasId, dados, legendaId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !podeCriarGrafico(canvasId, dados)) return;

    registrarGrafico(new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: dados.labels,
            datasets: [{
                data: dados.valores,
                backgroundColor: dados.labels.map((_, i) => PALETA[i % PALETA.length]),
                borderWidth: 0,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "66%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.parsed} registro(s)`,
                    },
                },
            },
        },
    }));

    montarLegenda(dados.labels, legendaId);
}

function montarLegenda(labels, legendaId) {
    const legenda = document.getElementById(legendaId);
    if (!legenda) return;

    legenda.innerHTML = "";
    labels.forEach((texto, i) => {
        const li = document.createElement("li");
        const dot = document.createElement("span");
        dot.className = "legend-dot";
        dot.style.background = PALETA[i % PALETA.length];
        li.appendChild(dot);
        li.append(texto);
        legenda.appendChild(li);
    });
}

function iniciarGraficos() {
    const configuracoes = [
        () => criarGraficoLinha("graficoPeriodo", window.DADOS_PERIODO, "Registros"),
        () => criarGraficoRosca("graficoSetor", window.DADOS_SETOR, "legendaSetor"),
        () => criarGraficoBarras("graficoRecurso", window.DADOS_RECURSO, "Reservas por recurso"),
        () => criarGraficoRosca("graficoStatus", window.DADOS_STATUS, "legendaStatus"),
        () => criarGraficoBarras("graficoResponsavel", window.DADOS_RESPONSAVEL, "Reservas por responsável"),
        () => criarGraficoBarras("graficoHora", window.DADOS_HORA, "Reservas por hora"),
    ];

    configuracoes.forEach((criar) => {
        try {
            criar();
        } catch (erro) {
            console.error("Falha ao montar um gráfico do relatório:", erro);
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciarGraficos);
} else {
    iniciarGraficos();
}

setInterval(() => {
    if (document.visibilityState === "visible") {
        window.location.reload();
    }
}, 60000);
