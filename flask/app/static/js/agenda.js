(function () {
    "use strict";

    const API_URL = "/api/agenda/compromissos";
    const DOCS_API_URL = "/api/agenda/documentacao";
    const DOCTORS_API_URL = "/api/agenda/medicos";
    const MINUTES_API_URL = "/api/agenda/atas";
    const EMAIL_SETTINGS_API_URL = "/api/configuracoes/avisos-documentacao";
    const EVALUATIONS_API_URL = "/api/avaliacoes";
    const THEME_KEY = "agendaTheme";
    const DOW = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
    const MONTHS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
    const WEEKDAY_FULL = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
    const STATUS_LABELS = {
        agendado: "Agendado",
        andamento: "Em andamento",
        cancelado: "Cancelado",
        concluido: "Concluído",
    };
    const DOCTOR_TYPE_LABELS = {
        credenciado: "Méd. credenciado",
        cooperado: "Méd. cooperado",
        laboratorio: "Laboratório",
        hospital: "Hospital",
        diagnostico: "Diagnóstico",
    };

    let state = {
        compromissos: [],
        calendarCursor: new Date(),
        selectedDate: toISODate(new Date()),
        deletingId: null,
        activeView: "agenda",
        documentacao: null,
        docsLoading: false,
        docsAlterados: new Map(),
        docsSalvando: new Set(),
        docsSaveTimers: new Map(),
        docsErros: new Set(),
        docsPage: 1,
        docsPageSize: 20,
        statusEditingId: null,
        disaccreditDoctor: null,
        atas: [],
        atasAnos: [],
        atasCarregadas: false,
        atasLoading: false,
        emailNotificationsEnabled: null,
        emailNotificationsLoading: false,
        avaliacoes: [],
        avaliacoesCarregadas: false,
        avaliacoesLoading: false,
        avaliacaoSelecionada: null,
        termoAdesao: null,
    };

    const el = {
        agendaTabs: document.querySelectorAll(".agenda-tab"),
        agendaView: document.getElementById("agendaView"),
        documentacaoView: document.getElementById("documentacaoView"),
        atasView: document.getElementById("atasView"),
        minutesOverlay: document.getElementById("minutesOverlay"),
        minutesForm: document.getElementById("minutesForm"),
        minutesFile: document.getElementById("minutesFile"),
        minutesFileName: document.getElementById("minutesFileName"),
        cancelMinutesBtn: document.getElementById("cancelMinutesBtn"),
        secondaryCancelMinutesBtn: document.getElementById("secondaryCancelMinutesBtn"),
        minutesTotal: document.getElementById("minutesTotal"),
        minutesLastUpdate: document.getElementById("minutesLastUpdate"),
        minutesSearch: document.getElementById("minutesSearch"),
        minutesYearFilter: document.getElementById("minutesYearFilter"),
        minutesTypeFilter: document.getElementById("minutesTypeFilter"),
        minutesOrder: document.getElementById("minutesOrder"),
        minutesList: document.getElementById("minutesList"),
        minutesFormError: document.getElementById("minutesFormError"),
        themeToggle: document.getElementById("themeToggle"),
        themeIconSun: document.getElementById("iconSun"),
        themeIconMoon: document.getElementById("iconMoon"),
        themeLabel: document.getElementById("themeLabel"),
        printBtn: document.getElementById("printBtn"),
        exportMonthPdfBtn: document.getElementById("exportMonthPdfBtn"),
        newApptBtn: document.getElementById("newApptBtn"),
        calMonthLabel: document.getElementById("calMonthLabel"),
        calGrid: document.getElementById("calGrid"),
        prevMonth: document.getElementById("prevMonth"),
        nextMonth: document.getElementById("nextMonth"),
        myPicker: document.getElementById("myPicker"),
        myYearLabel: document.getElementById("myYearLabel"),
        myGrid: document.getElementById("myGrid"),
        myPrevYear: document.getElementById("myPrevYear"),
        myNextYear: document.getElementById("myNextYear"),
        filterResponsavel: document.getElementById("filterResponsavel"),
        filterStatus: document.getElementById("filterStatus"),
        selectedDateTitle: document.getElementById("selectedDateTitle"),
        selectedDateSub: document.getElementById("selectedDateSub"),
        daySummary: document.getElementById("daySummary"),
        apptList: document.getElementById("apptList"),
        searchInput: document.getElementById("searchInput"),
        feedback: document.getElementById("feedbackMessage"),
        modalOverlay: document.getElementById("modalOverlay"),
        modalTitle: document.getElementById("modalTitle"),
        apptForm: document.getElementById("apptForm"),
        apptFormError: document.getElementById("apptFormError"),
        apptId: document.getElementById("apptId"),
        fTitulo: document.getElementById("fTitulo"),
        fData: document.getElementById("fData"),
        fHoraInicio: document.getElementById("fHoraInicio"),
        fHoraFim: document.getElementById("fHoraFim"),
        fResponsavel: document.getElementById("fResponsavel"),
        fLocal: document.getElementById("fLocal"),
        fStatus: document.getElementById("fStatus"),
        fDescricao: document.getElementById("fDescricao"),
        respList: document.getElementById("respList"),
        cancelModalBtn: document.getElementById("cancelModalBtn"),
        secondaryCancelModalBtn: document.getElementById("secondaryCancelModalBtn"),
        confirmOverlay: document.getElementById("confirmOverlay"),
        cancelDeleteBtn: document.getElementById("cancelDeleteBtn"),
        confirmDeleteBtn: document.getElementById("confirmDeleteBtn"),
        statusOverlay: document.getElementById("statusOverlay"),
        cancelStatusBtn: document.getElementById("cancelStatusBtn"),
        doctorOverlay: document.getElementById("doctorOverlay"),
        doctorForm: document.getElementById("doctorForm"),
        doctorName: document.getElementById("doctorName"),
        doctorType: document.getElementById("doctorType"),
        doctorEmail: document.getElementById("doctorEmail"),
        doctorFormError: document.getElementById("doctorFormError"),
        cancelDoctorBtn: document.getElementById("cancelDoctorBtn"),
        secondaryCancelDoctorBtn: document.getElementById("secondaryCancelDoctorBtn"),
        newDocsBtn: document.getElementById("newDocsBtn"),
        docsEmailGlobalControl: document.getElementById("docsEmailGlobalControl"),
        docsEmailGlobalStatus: document.getElementById("docsEmailGlobalStatus"),
        docsEmailGlobalButton: document.getElementById("docsEmailGlobalButton"),
        docsDirtyCount: document.getElementById("docsDirtyCount"),
        docsPercentText: document.getElementById("docsPercentText"),
        docsSummary: document.getElementById("docsSummary"),
        docsExpiryAlert: document.getElementById("docsExpiryAlert"),
        docsCategoryFilter: document.getElementById("docsCategoryFilter"),
        docsStatusFilter: document.getElementById("docsStatusFilter"),
        docsSearchInput: document.getElementById("docsSearchInput"),
        docsResultCount: document.getElementById("docsResultCount"),
        docsDoctorsList: document.getElementById("docsDoctorsList"),
        docsPagination: document.getElementById("docsPagination"),
        docsPrevPage: document.getElementById("docsPrevPage"),
        docsNextPage: document.getElementById("docsNextPage"),
        docsPageInfo: document.getElementById("docsPageInfo"),
        disaccreditOverlay: document.getElementById("disaccreditOverlay"),
        disaccreditForm: document.getElementById("disaccreditForm"),
        disaccreditDoctorName: document.getElementById("disaccreditDoctorName"),
        disaccreditReason: document.getElementById("disaccreditReason"),
        disaccreditFile: document.getElementById("disaccreditFile"),
        disaccreditFormError: document.getElementById("disaccreditFormError"),
        cancelDisaccreditBtn: document.getElementById("cancelDisaccreditBtn"),
        secondaryCancelDisaccreditBtn: document.getElementById("secondaryCancelDisaccreditBtn"),
        evaluationNewTrigger: document.getElementById("evaluationNewTrigger"),
        evaluationNewOverlay: document.querySelector(".evaluation-new-overlay"),
        evaluationModalCloseButtons: document.querySelectorAll("[data-evaluation-modal-close]"),
        evaluationProcessItems: document.getElementById("evaluationProcessItems"),
        evaluationProcessList: document.getElementById("evaluationProcessList"),
        evaluationProcessDetail: document.getElementById("evaluationProcessDetail"),
        evaluationProviderSelect: document.getElementById("evaluationProviderSelect"),
        evaluationStartButton: document.getElementById("evaluationStartButton"),
        evaluationNewError: document.getElementById("evaluationNewError"),
        evaluationSelectedAvatar: document.getElementById("evaluationSelectedAvatar"),
        evaluationSelectedName: document.getElementById("evaluationSelectedName"),
        evaluationSelectedSubtitle: document.getElementById("evaluationSelectedSubtitle"),
        evaluationSelectedStage: document.getElementById("evaluationSelectedStage"),
        evaluationStepTerm: document.getElementById("evaluationStepTerm"),
        evaluationStepChecklist: document.getElementById("evaluationStepChecklist"),
        evaluationStepFeedback: document.getElementById("evaluationStepFeedback"),
        evaluationTermStatus: document.getElementById("evaluationTermStatus"),
        evaluationTermFile: document.getElementById("evaluationTermFile"),
        evaluationTermFileName: document.getElementById("evaluationTermFileName"),
        evaluationTermDownload: document.getElementById("evaluationTermDownload"),
        evaluationTermMessage: document.getElementById("evaluationTermMessage"),
        evaluationTermSaveButton: document.getElementById("evaluationTermSaveButton"),
        evaluationTermPositions: document.querySelectorAll('[name="evaluationTermPosition"]'),
    };

    function toISODate(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    }

    function adicionarDiasDataISO(valor, dias) {
        const [ano, mes, dia] = (valor || "").split("-").map(Number);
        if (!ano || !mes || !dia) return "";
        const data = new Date(Date.UTC(ano, mes - 1, dia));
        data.setUTCDate(data.getUTCDate() + dias);
        return data.toISOString().slice(0, 10);
    }

    function parseISODate(value) {
        const [year, month, day] = value.split("-").map(Number);
        return new Date(year, month - 1, day);
    }

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value == null ? "" : String(value);
        return div.innerHTML;
    }

    function showFeedback(message, type = "success") {
        el.feedback.textContent = message;
        el.feedback.className = `feedback ${type}`;
        window.clearTimeout(showFeedback.timer);
        showFeedback.timer = window.setTimeout(() => {
            el.feedback.className = "feedback hidden";
        }, 4200);
    }

    function limparErroCompromisso() {
        el.apptFormError.textContent = "";
        el.apptFormError.classList.add("hidden");
    }

    function mostrarErroCompromisso(message) {
        el.apptFormError.textContent = message;
        el.apptFormError.classList.remove("hidden");
    }

    function switchView(view) {
        state.activeView = view;
        el.agendaTabs.forEach((tab) => {
            tab.classList.toggle("active", tab.dataset.view === view);
        });
        el.agendaView.classList.toggle("active", view === "agenda");
        el.documentacaoView.classList.toggle("active", view === "documentacao");
        el.atasView.classList.toggle("active", view === "atas");

        if (view === "documentacao" && !state.documentacao && !state.docsLoading) {
            carregarDocumentacao();
        }
        if (view === "documentacao" && state.emailNotificationsEnabled === null && !state.emailNotificationsLoading) {
            carregarEstadoAvisosGlobais();
        }
        if (view === "atas" && !state.atasCarregadas && !state.atasLoading) {
            carregarAtas();
        }
        if (view === "avaliacao" && !state.avaliacoesCarregadas && !state.avaliacoesLoading) {
            carregarAvaliacoes();
        }
    }

    function abrirFormularioAta() {
        el.minutesOverlay.classList.add("open");
        window.setTimeout(() => document.getElementById("minutesNumber")?.focus(), 50);
    }

    function fecharFormularioAta() {
        el.minutesOverlay.classList.remove("open");
        el.minutesFormError.textContent = "";
        el.minutesFormError.classList.add("hidden");
    }

    function normalizarBuscaAta(valor) {
        return String(valor || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase();
    }

    async function carregarAtas() {
        state.atasLoading = true;
        el.minutesList.innerHTML = '<div class="minutes-empty"><p>Carregando atas...</p></div>';
        try {
            const dados = await requestJson(MINUTES_API_URL);
            state.atas = dados.registros || [];
            state.atasAnos = dados.anos || [];
            state.atasCarregadas = true;
            el.minutesTotal.textContent = String(dados.total || 0);
            el.minutesLastUpdate.textContent = dados.ultimaAtualizacao || "Nenhuma";
            atualizarFiltroAnosAtas();
            renderAtas();
        } catch (error) {
            el.minutesList.innerHTML = `<div class="minutes-empty"><h3>Não foi possível carregar as atas</h3><p>${escapeHtml(error.message)}</p></div>`;
        } finally {
            state.atasLoading = false;
        }
    }

    function atualizarFiltroAnosAtas() {
        const atual = el.minutesYearFilter.value;
        el.minutesYearFilter.innerHTML = '<option value="">Todos os anos</option>' +
            state.atasAnos.map((ano) => `<option value="${ano}">${ano}</option>`).join("");
        if (state.atasAnos.map(String).includes(atual)) el.minutesYearFilter.value = atual;
    }

    function atasFiltradas() {
        const busca = normalizarBuscaAta(el.minutesSearch.value.trim());
        const ano = el.minutesYearFilter.value;
        const tipo = el.minutesTypeFilter.value;
        const resultado = state.atas.filter((ata) => {
            if (ano && String(ata.ano) !== ano) return false;
            if (tipo && ata.tipo !== tipo) return false;
            if (!busca) return true;
            return normalizarBuscaAta([
                ata.numero,
                ata.tipoTexto,
                ata.pauta,
                ata.participantes,
                ata.arquivo?.nome,
            ].join(" ")).includes(busca);
        });
        resultado.sort((a, b) => {
            const comparacao = String(a.data).localeCompare(String(b.data));
            return el.minutesOrder.value === "antigas" ? comparacao : -comparacao;
        });
        return resultado;
    }

    function renderAtas() {
        const atas = atasFiltradas();
        if (!atas.length) {
            const temAtas = state.atas.length > 0;
            el.minutesList.innerHTML = `
                <div class="minutes-empty">
                    <span class="minutes-empty-icon">
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M6 3h9l3 3v15H6V3Zm8 0v4h4M9 12h6M9 16h4"/>
                        </svg>
                    </span>
                    <h3>${temAtas ? "Nenhuma ata encontrada" : "Nenhuma ata anexada"}</h3>
                    <p>${temAtas ? "Ajuste os filtros para encontrar outros registros." : "Quando as atas forem adicionadas, elas aparecerão organizadas neste espaço."}</p>
                    ${temAtas ? "" : '<button class="btn" data-action="open-minutes-form" type="button">Anexar primeira ata</button>'}
                </div>`;
        } else {
            el.minutesList.innerHTML = atas.map((ata) => `
                <article class="minutes-card" data-id="${ata.id}">
                    <div class="minutes-card-icon">
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M6 3h9l3 3v15H6V3Zm8 0v4h4M9 12h6M9 16h4"/>
                        </svg>
                    </div>
                    <div class="minutes-card-content">
                        <div class="minutes-card-top">
                            <span class="minutes-type-badge">${escapeHtml(ata.tipoTexto)}</span>
                            <time datetime="${escapeHtml(ata.data)}">${escapeHtml(ata.dataTexto)}</time>
                        </div>
                        <h3>Ata nº ${escapeHtml(ata.numero)}</h3>
                        <p class="minutes-card-agenda">${escapeHtml(ata.pauta)}</p>
                        <p class="minutes-card-participants"><strong>Participantes:</strong> ${escapeHtml(ata.participantes)}</p>
                        <span class="minutes-card-file">${escapeHtml(ata.arquivo?.nome || "")}</span>
                    </div>
                    <div class="minutes-card-actions">
                        <a class="btn" href="${escapeHtml(ata.arquivo?.url || "#")}">Baixar</a>
                        <button class="minutes-delete-btn" data-action="delete-minute" data-id="${ata.id}" type="button" aria-label="Apagar ata" title="Apagar ata">
                            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-1 11H8L7 9Z"/></svg>
                        </button>
                    </div>
                </article>
            `).join("");
        }

        el.minutesList.querySelectorAll('[data-action="open-minutes-form"]').forEach((button) => {
            button.addEventListener("click", abrirFormularioAta);
        });
        el.minutesList.querySelectorAll('[data-action="delete-minute"]').forEach((button) => {
            button.addEventListener("click", () => excluirAta(Number(button.dataset.id)));
        });
    }

    async function salvarAta(event) {
        event.preventDefault();
        el.minutesFormError.textContent = "";
        el.minutesFormError.classList.add("hidden");

        const submit = el.minutesForm.querySelector('button[type="submit"]');
        const formData = new FormData();
        formData.append("numero", document.getElementById("minutesNumber").value.trim());
        formData.append("data", document.getElementById("minutesDate").value);
        formData.append("tipo", document.getElementById("minutesType").value);
        formData.append("pauta", document.getElementById("minutesAgenda").value.trim());
        formData.append("participantes", document.getElementById("minutesParticipants").value.trim());
        formData.append("arquivo", el.minutesFile.files[0]);

        submit.disabled = true;
        submit.textContent = "Adicionando...";
        try {
            const response = await fetch(MINUTES_API_URL, {
                method: "POST",
                headers: { Accept: "application/json" },
                body: formData,
            });
            const ata = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(ata.erro || "Não foi possível adicionar a ata.");

            el.minutesForm.reset();
            el.minutesFileName.textContent = "PDF, DOC ou DOCX";
            fecharFormularioAta();
            await carregarAtas();
            showFeedback("Ata adicionada com sucesso.");
        } catch (error) {
            el.minutesFormError.textContent = error.message;
            el.minutesFormError.classList.remove("hidden");
        } finally {
            submit.disabled = false;
            submit.textContent = "Adicionar ata";
        }
    }

    async function excluirAta(id) {
        if (!window.confirm("Deseja apagar esta ata e o arquivo anexado?")) return;
        try {
            await requestJson(`${MINUTES_API_URL}/${id}`, { method: "DELETE" });
            await carregarAtas();
            showFeedback("Ata apagada com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    function atualizarControleTema(theme) {
        const usarModoClaro = theme === "dark";
        el.themeIconSun.hidden = !usarModoClaro;
        el.themeIconMoon.hidden = usarModoClaro;
        el.themeLabel.textContent = usarModoClaro ? "Modo claro" : "Modo escuro";
        el.themeToggle.setAttribute("aria-label", usarModoClaro
            ? "Alternar para o modo claro"
            : "Alternar para o modo escuro");
        el.themeToggle.title = usarModoClaro ? "Modo claro" : "Modo escuro";
    }

    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY) || localStorage.getItem("theme") || "dark";
        document.documentElement.setAttribute("data-theme", saved);
        atualizarControleTema(saved);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute("data-theme") || "dark";
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem(THEME_KEY, next);
        atualizarControleTema(next);
    }

    async function requestJson(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            ...options,
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.erro || data.error || "Não foi possível concluir a ação.");
        }

        return data;
    }

    const EVALUATION_STAGE_LABELS = {
        termo_adesao: "Termo de adesão",
        checklist: "Checklist",
        feedback: "Feedback",
        concluida: "Concluída",
        concluido: "Concluída",
    };

    function evaluationInitials(name) {
        return String(name || "")
            .trim()
            .split(/\s+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part[0].toUpperCase())
            .join("") || "--";
    }

    function evaluationProgress(item) {
        if (item.status === "concluida" || item.status === "concluido") return { percent: 100, text: "3 de 3 etapas" };
        if (item.etapaAtual === "feedback") return { percent: 100, text: "3 de 3 etapas" };
        if (item.etapaAtual === "checklist") return { percent: 66, text: "2 de 3 etapas" };
        return { percent: 33, text: "1 de 3 etapas" };
    }

    function formatEvaluationDate(value) {
        if (!value) return "Sem atualização";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "Sem atualização";
        return new Intl.DateTimeFormat("pt-BR", {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }).format(date);
    }

    function setEvaluationMessage(element, message = "", type = "error") {
        if (!element) return;
        element.textContent = message;
        element.className = `evaluation-form-message ${type}`;
        element.classList.toggle("hidden", !message);
    }

    function renderAvaliacoes() {
        if (!el.evaluationProcessItems) return;
        if (!state.avaliacoes.length) {
            el.evaluationProcessItems.innerHTML = '<div class="evaluation-list-message">Nenhuma avaliação iniciada. Clique em “Iniciar nova avaliação” para começar.</div>';
            return;
        }

        el.evaluationProcessItems.innerHTML = state.avaliacoes.map((item) => {
            const complete = item.status === "concluida" || item.status === "concluido";
            const progress = evaluationProgress(item);
            return `
                <article class="evaluation-process-item${complete ? " is-complete" : ""}">
                    <div class="evaluation-process-provider"><i>${escapeHtml(evaluationInitials(item.prestadorNome))}</i><span><strong>${escapeHtml(item.prestadorNome)}</strong><small>${escapeHtml(item.categoriaNome || "Sem categoria")}</small></span></div>
                    <span class="evaluation-process-stage${complete ? " is-complete" : item.etapaAtual === "checklist" ? " is-progress" : ""}">${escapeHtml(EVALUATION_STAGE_LABELS[item.etapaAtual] || item.etapaAtual)}</span>
                    <div class="evaluation-process-progress"><span><i style="width: ${progress.percent}%"></i></span><small>${progress.text}</small></div>
                    <time>${escapeHtml(formatEvaluationDate(item.atualizadoEm || item.iniciadoEm))}</time>
                    <button class="btn evaluation-continue-button" type="button" data-evaluation-open="${Number(item.id)}">${complete ? "Visualizar" : "Continuar"}</button>
                </article>`;
        }).join("");
    }

    async function carregarAvaliacoes(force = false) {
        if (state.avaliacoesLoading || (state.avaliacoesCarregadas && !force)) return;
        state.avaliacoesLoading = true;
        if (!state.avaliacoesCarregadas && el.evaluationProcessItems) {
            el.evaluationProcessItems.innerHTML = '<div class="evaluation-list-message">Carregando avaliações...</div>';
        }
        try {
            const data = await requestJson(EVALUATIONS_API_URL);
            state.avaliacoes = Array.isArray(data.registros) ? data.registros : [];
            state.avaliacoesCarregadas = true;
            renderAvaliacoes();
        } catch (error) {
            if (el.evaluationProcessItems) el.evaluationProcessItems.innerHTML = `<div class="evaluation-list-message is-error">${escapeHtml(error.message)}</div>`;
        } finally {
            state.avaliacoesLoading = false;
        }
    }

    function closeEvaluationModal() {
        el.evaluationNewOverlay?.classList.remove("open");
        document.body.classList.remove("modal-open");
        setEvaluationMessage(el.evaluationNewError);
    }

    async function openEvaluationModal() {
        if (!el.evaluationNewOverlay) return;
        el.evaluationNewOverlay.classList.add("open");
        document.body.classList.add("modal-open");
        setEvaluationMessage(el.evaluationNewError);
        el.evaluationProviderSelect.disabled = true;
        el.evaluationStartButton.disabled = true;
        el.evaluationProviderSelect.innerHTML = '<option value="">Carregando cadastros...</option>';
        try {
            const data = await requestJson(`${EVALUATIONS_API_URL}/cadastros-disponiveis`);
            const providers = Array.isArray(data.registros) ? data.registros : [];
            el.evaluationProviderSelect.innerHTML = providers.length
                ? '<option value="">Selecione um cadastro</option>' + providers.map((provider) => `<option value="${Number(provider.id)}">${escapeHtml(provider.nome)} — ${escapeHtml(provider.categoriaNome || "Sem categoria")}</option>`).join("")
                : '<option value="">Nenhum cadastro disponível</option>';
            el.evaluationProviderSelect.disabled = !providers.length;
        } catch (error) {
            el.evaluationProviderSelect.innerHTML = '<option value="">Não foi possível carregar</option>';
            setEvaluationMessage(el.evaluationNewError, error.message);
        }
    }

    async function iniciarAvaliacao() {
        const providerId = Number(el.evaluationProviderSelect?.value);
        if (!providerId) {
            setEvaluationMessage(el.evaluationNewError, "Selecione um cadastro para iniciar a avaliação.");
            return;
        }
        el.evaluationStartButton.disabled = true;
        el.evaluationStartButton.textContent = "Iniciando...";
        try {
            const evaluation = await requestJson(EVALUATIONS_API_URL, {
                method: "POST",
                body: JSON.stringify({ prestadorId: providerId }),
            });
            closeEvaluationModal();
            state.avaliacoesCarregadas = false;
            await carregarAvaliacoes(true);
            await abrirAvaliacao(evaluation.id);
            showFeedback("Avaliação iniciada com sucesso.");
        } catch (error) {
            setEvaluationMessage(el.evaluationNewError, error.message);
        } finally {
            el.evaluationStartButton.textContent = "Iniciar avaliação";
            el.evaluationStartButton.disabled = !el.evaluationProviderSelect?.value;
        }
    }

    function renderTermoAdesao() {
        const term = state.termoAdesao;
        el.evaluationTermPositions.forEach((input) => {
            input.checked = term?.posicionamento === input.value;
        });
        el.evaluationTermFile.value = "";
        el.evaluationTermFileName.textContent = term?.arquivo?.nome || "Nenhum arquivo selecionado";
        el.evaluationTermStatus.textContent = term ? "Termo registrado" : "Aguardando preenchimento";
        if (term?.arquivo?.url) {
            el.evaluationTermDownload.href = term.arquivo.url;
            el.evaluationTermDownload.classList.remove("hidden");
        } else {
            el.evaluationTermDownload.href = "#";
            el.evaluationTermDownload.classList.add("hidden");
        }
        setEvaluationMessage(el.evaluationTermMessage);
    }

    function renderAvaliacaoSelecionada() {
        const item = state.avaliacaoSelecionada;
        if (!item) return;
        el.evaluationSelectedAvatar.textContent = evaluationInitials(item.prestadorNome);
        el.evaluationSelectedName.textContent = item.prestadorNome;
        el.evaluationSelectedSubtitle.textContent = `${item.categoriaNome || "Sem categoria"} • ${item.status === "em_andamento" ? "Processo em andamento" : "Processo concluído"}`;
        el.evaluationSelectedStage.textContent = EVALUATION_STAGE_LABELS[item.etapaAtual] || item.etapaAtual;
        renderTermoAdesao();
    }

    async function abrirAvaliacao(id) {
        try {
            const [evaluation, termData] = await Promise.all([
                requestJson(`${EVALUATIONS_API_URL}/${id}`),
                requestJson(`${EVALUATIONS_API_URL}/${id}/termo`),
            ]);
            state.avaliacaoSelecionada = evaluation;
            state.termoAdesao = termData.termo || null;
            renderAvaliacaoSelecionada();
            el.evaluationProcessDetail.checked = true;
            if (evaluation.etapaAtual === "feedback") el.evaluationStepFeedback.checked = true;
            else if (evaluation.etapaAtual === "checklist") el.evaluationStepChecklist.checked = true;
            else el.evaluationStepTerm.checked = true;
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    async function salvarTermoAdesao() {
        const evaluation = state.avaliacaoSelecionada;
        const position = Array.from(el.evaluationTermPositions).find((input) => input.checked)?.value;
        if (!evaluation) return;
        if (!position) {
            setEvaluationMessage(el.evaluationTermMessage, "Selecione o posicionamento do cadastro.");
            return;
        }
        const file = el.evaluationTermFile.files?.[0];
        if (!file && !state.termoAdesao?.arquivo) {
            setEvaluationMessage(el.evaluationTermMessage, "Anexe o documento do termo de adesão.");
            return;
        }
        const formData = new FormData();
        formData.append("posicionamento", position);
        if (file) formData.append("arquivo", file);
        el.evaluationTermSaveButton.disabled = true;
        el.evaluationTermSaveButton.textContent = "Salvando...";
        setEvaluationMessage(el.evaluationTermMessage);
        try {
            const response = await fetch(`${EVALUATIONS_API_URL}/${evaluation.id}/termo`, {
                method: "PUT",
                headers: { Accept: "application/json" },
                body: formData,
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.erro || "Não foi possível salvar o termo.");
            state.termoAdesao = data;
            state.avaliacaoSelecionada.etapaAtual = data.avaliacaoEtapaAtual || "checklist";
            renderAvaliacaoSelecionada();
            el.evaluationStepChecklist.checked = true;
            state.avaliacoesCarregadas = false;
            await carregarAvaliacoes(true);
            showFeedback("Termo de adesão salvo com sucesso.");
        } catch (error) {
            setEvaluationMessage(el.evaluationTermMessage, error.message);
        } finally {
            el.evaluationTermSaveButton.disabled = false;
            el.evaluationTermSaveButton.textContent = "Salvar e continuar";
        }
    }

    function renderEstadoAvisosGlobais() {
        if (!el.docsEmailGlobalControl) return;

        const enabled = state.emailNotificationsEnabled;
        const loading = state.emailNotificationsLoading;
        el.docsEmailGlobalControl.classList.toggle("is-active", enabled === true);
        el.docsEmailGlobalControl.classList.toggle("is-paused", enabled === false);
        el.docsEmailGlobalButton.disabled = loading;

        if (loading) {
            el.docsEmailGlobalStatus.textContent = "Consultando envios...";
            el.docsEmailGlobalButton.textContent = "Aguarde...";
            return;
        }

        if (enabled === null) {
            el.docsEmailGlobalStatus.textContent = "Não foi possível consultar os envios";
            el.docsEmailGlobalButton.textContent = "Tentar novamente";
            return;
        }

        el.docsEmailGlobalStatus.textContent = enabled
            ? "Envios automáticos ativos"
            : "Todos os envios estão pausados";
        el.docsEmailGlobalButton.textContent = enabled
            ? "Pausar todos"
            : "Ativar todos";
    }

    async function carregarEstadoAvisosGlobais() {
        state.emailNotificationsLoading = true;
        renderEstadoAvisosGlobais();

        try {
            const result = await requestJson(EMAIL_SETTINGS_API_URL);
            state.emailNotificationsEnabled = Boolean(result.ativo);
        } catch (error) {
            state.emailNotificationsEnabled = null;
            showFeedback(error.message, "error");
        } finally {
            state.emailNotificationsLoading = false;
            renderEstadoAvisosGlobais();
        }
    }

    async function alternarAvisosGlobais() {
        if (state.emailNotificationsEnabled === null) {
            await carregarEstadoAvisosGlobais();
            return;
        }

        const enabled = !state.emailNotificationsEnabled;
        if (!enabled && !window.confirm("Deseja pausar os avisos de documentação para todos os cadastros?")) return;

        state.emailNotificationsLoading = true;
        renderEstadoAvisosGlobais();
        try {
            const result = await requestJson(EMAIL_SETTINGS_API_URL, {
                method: "PATCH",
                body: JSON.stringify({ ativo: enabled }),
            });
            state.emailNotificationsEnabled = Boolean(result.ativo);
            showFeedback(result.ativo
                ? "Os avisos de documentação foram ativados para todos."
                : "Os avisos de documentação foram pausados para todos.");
        } catch (error) {
            showFeedback(error.message, "error");
        } finally {
            state.emailNotificationsLoading = false;
            renderEstadoAvisosGlobais();
        }
    }

    async function enviarArquivoDocumentacao(id, input) {
        const arquivo = input.files?.[0];
        if (!arquivo) return;

        const area = input.closest(".docs-file-area");
        const botao = area.querySelector(".docs-file-button");
        const formData = new FormData();
        formData.append("arquivo", arquivo);
        botao.classList.add("uploading");
        botao.textContent = "Enviando...";
        input.disabled = true;

        try {
            const response = await fetch(`${DOCS_API_URL}/${id}/arquivo`, {
                method: "POST",
                headers: { Accept: "application/json" },
                body: formData,
            });
            const documento = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(documento.erro || "Não foi possível anexar o arquivo.");
            }

            aplicarDocumentoSalvo(documento);
            area.querySelector(".docs-file-name").textContent = documento.arquivo.nome;
            const download = area.querySelector(".docs-file-download");
            download.href = documento.arquivo.url;
            download.classList.remove("hidden");
            botao.textContent = "Substituir arquivo";
            showFeedback("Arquivo anexado com sucesso.");
        } catch (error) {
            botao.textContent = area.dataset.hasFile === "true" ? "Substituir arquivo" : "Anexar arquivo";
            showFeedback(error.message, "error");
        } finally {
            area.dataset.hasFile = area.querySelector(".docs-file-download").classList.contains("hidden") ? "false" : "true";
            botao.classList.remove("uploading");
            input.disabled = false;
            input.value = "";
        }
    }

    async function carregarCompromissos() {
        try {
            state.compromissos = await requestJson(API_URL);
            refreshResponsavelFilter();
            renderCalendar();
            renderDay();
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    async function carregarDocumentacao(force = false) {
        if (state.documentacao && !force) {
            renderDocumentacao();
            return;
        }

        state.docsLoading = true;
        el.docsDoctorsList.innerHTML = `<div class="docs-empty">Carregando documentação...</div>`;

        try {
            state.documentacao = await requestJson(DOCS_API_URL);
            state.docsAlterados.clear();
            renderDocumentacao();
        } catch (error) {
            el.docsDoctorsList.innerHTML = `<div class="docs-empty">${escapeHtml(error.message)}</div>`;
        } finally {
            state.docsLoading = false;
        }
    }

    function documentosFiltrados() {
        const dados = state.documentacao?.registros || [];
        const status = el.docsStatusFilter.value;
        const busca = el.docsSearchInput.value.trim().toLowerCase();

        return dados.filter((item) => {
            const statusItem = (item.status || "").trim().toUpperCase();
            if (status && statusItem !== status) return false;
            if (!busca) return true;

            return [
                item.medico,
                item.nome,
                ...(item.valores || []),
            ].join(" ").toLowerCase().includes(busca);
        });
    }

    function medicosFiltrados() {
        const grupos = new Map();
        const statusFiltro = el.docsStatusFilter.value;
        const busca = el.docsSearchInput.value.trim().toLowerCase();
        const categoria = el.docsCategoryFilter.value;
        const mostrarDescredenciados = categoria === "descredenciados";
        const catalogo = new Map(
            (state.documentacao?.medicos || []).map((medico) => [medico.nome.toLowerCase(), medico])
        );

        if (!statusFiltro) {
            (state.documentacao?.medicos || []).forEach((medico) => {
                if (Boolean(medico.descredenciado) !== mostrarDescredenciados) return;
                if (!mostrarDescredenciados && categoria !== "todos" && (medico.tipo || "credenciado") !== categoria) return;
                if (busca && !medico.nome.toLowerCase().includes(busca)) return;
                grupos.set(medico.nome, {
                    id: medico.id,
                    nome: medico.nome,
                    tipo: medico.tipo || "credenciado",
                    descredenciado: Boolean(medico.descredenciado),
                    emailNotificacao: medico.emailNotificacao || "",
                    receberAvisos: Boolean(medico.receberAvisos),
                    motivoDescredenciamento: medico.motivoDescredenciamento || "",
                    arquivoDescredenciamento: medico.arquivoDescredenciamento || null,
                    documentos: [],
                    conformes: 0,
                    pendentes: 0,
                    notificados: 0,
                    naoIndicados: 0,
                });
            });
        }

        documentosFiltrados().forEach((item) => {
            const medico = item.medico || item.nome || "Sem médico informado";
            const cadastro = catalogo.get(medico.toLowerCase());
            const tipo = cadastro?.tipo || "credenciado";
            if (Boolean(cadastro?.descredenciado) !== mostrarDescredenciados) return;
            if (!mostrarDescredenciados && categoria !== "todos" && tipo !== categoria) return;
            if (!grupos.has(medico)) {
                grupos.set(medico, {
                    id: cadastro?.id || null,
                    nome: medico,
                    tipo,
                    descredenciado: Boolean(cadastro?.descredenciado),
                    emailNotificacao: cadastro?.emailNotificacao || "",
                    receberAvisos: Boolean(cadastro?.receberAvisos),
                    motivoDescredenciamento: cadastro?.motivoDescredenciamento || "",
                    arquivoDescredenciamento: cadastro?.arquivoDescredenciamento || null,
                    documentos: [],
                    conformes: 0,
                    pendentes: 0,
                    notificados: 0,
                });
            }

            const grupo = grupos.get(medico);
            grupo.documentos.push(item);
            if (item.naoIndicado) {
                grupo.naoIndicados += 1;
                return;
            }
            const status = (item.status || "").trim().toUpperCase();
            if (status === "CONFORME") grupo.conformes += 1;
            if (status === "PENDENTE") grupo.pendentes += 1;
            if (status === "NOTIFICADO") grupo.notificados += 1;
        });

        return Array.from(grupos.values()).sort((a, b) => a.nome.localeCompare(b.nome));
    }

    function atualizarContadorAlteracoes() {
        el.docsDirtyCount.classList.remove("saving", "saved", "error");

        if (state.docsSalvando.size > 0 || state.docsSaveTimers.size > 0) {
            el.docsDirtyCount.textContent = "Salvando...";
            el.docsDirtyCount.classList.add("saving");
        } else if (state.docsErros.size > 0) {
            el.docsDirtyCount.textContent = "Erro ao salvar — tente novamente";
            el.docsDirtyCount.classList.add("error");
        } else if (state.docsAlterados.size > 0) {
            el.docsDirtyCount.textContent = "Alterações pendentes...";
            el.docsDirtyCount.classList.add("saving");
        } else {
            el.docsDirtyCount.textContent = "Alterações salvas automaticamente";
            el.docsDirtyCount.classList.add("saved");
        }
    }

    function registrarAlteracaoDocumento(id, payload, row) {
        const atual = state.docsAlterados.get(id) || {};
        state.docsAlterados.set(id, { ...atual, ...payload });
        state.docsErros.delete(id);
        if (row) row.classList.add("edited");
        atualizarContadorAlteracoes();
    }

    function agendarSalvamentoDocumento(id, delay = 700) {
        const timerAnterior = state.docsSaveTimers.get(id);
        if (timerAnterior) clearTimeout(timerAnterior);

        const timer = window.setTimeout(() => {
            state.docsSaveTimers.delete(id);
            salvarDocumentoAutomaticamente(id);
        }, delay);

        state.docsSaveTimers.set(id, timer);
        atualizarContadorAlteracoes();
    }

    function salvarDocumentoAgora(id) {
        const timer = state.docsSaveTimers.get(id);
        if (timer) {
            clearTimeout(timer);
            state.docsSaveTimers.delete(id);
        }
        atualizarContadorAlteracoes();
        return salvarDocumentoAutomaticamente(id);
    }

    function aplicarDocumentoSalvo(documento) {
        const registros = state.documentacao?.registros || [];
        const index = registros.findIndex((item) => item.id === documento.id);
        if (index >= 0) registros[index] = documento;
        const resumo = state.documentacao?.resumo;
        if (resumo) {
            const avaliados = registros.filter((item) => !item.naoIndicado);
            resumo.total = avaliados.length;
            resumo.naoIndicados = registros.length - avaliados.length;
            resumo.conformes = avaliados.filter((item) => item.status === "CONFORME").length;
            resumo.pendentes = avaliados.filter((item) => item.status === "PENDENTE").length;
            resumo.notificados = avaliados.filter((item) => item.status === "NOTIFICADO").length;
            state.documentacao.percentualTexto = resumo.total
                ? `${(resumo.conformes / resumo.total * 100).toFixed(2).replace(".", ",")}%`
                : "0,00%";
            renderResumoDocumentacao();
        }

        const row = el.docsDoctorsList.querySelector(`[data-id="${documento.id}"]`);
        const statusButton = row?.querySelector('[data-action="choose-status"]');
        if (statusButton) {
            statusButton.textContent = documento.status || "-";
            statusButton.className = `docs-status-cell ${normalizarClasseStatus(documento.status)}`;
        }
        const naoIndicadoInput = row?.querySelector('input[data-field="naoIndicado"]');
        if (naoIndicadoInput) {
            naoIndicadoInput.checked = Boolean(documento.naoIndicado);
            row.classList.toggle("is-not-indicated", Boolean(documento.naoIndicado));
        }
    }

    async function salvarDocumentoAutomaticamente(id) {
        if (state.docsSalvando.has(id) || !state.docsAlterados.has(id)) return;

        state.docsSalvando.add(id);
        atualizarContadorAlteracoes();

        try {
            while (state.docsAlterados.has(id)) {
                const payload = state.docsAlterados.get(id);
                state.docsAlterados.delete(id);

                try {
                    const documentoSalvo = await requestJson(`${DOCS_API_URL}/${id}`, {
                        method: "PATCH",
                        body: JSON.stringify(payload),
                        keepalive: true,
                    });
                    aplicarDocumentoSalvo(documentoSalvo);
                    state.docsErros.delete(id);
                } catch (error) {
                    const maisRecentes = state.docsAlterados.get(id) || {};
                    state.docsAlterados.set(id, { ...payload, ...maisRecentes });
                    throw error;
                }
            }

            const row = el.docsDoctorsList.querySelector(`[data-id="${id}"]`);
            if (row) row.classList.remove("edited");
        } catch (error) {
            state.docsErros.add(id);
            showFeedback(`Não foi possível salvar automaticamente: ${error.message}`, "error");
        } finally {
            state.docsSalvando.delete(id);
            atualizarContadorAlteracoes();
        }
    }

    async function tentarSalvarDocumentosPendentes() {
        const ids = Array.from(state.docsAlterados.keys());
        await Promise.all(ids.map((id) => salvarDocumentoAutomaticamente(id)));
    }

    function renderResumoDocumentacao() {
        const categoria = el.docsCategoryFilter.value;
        const catalogo = new Map(
            (state.documentacao?.medicos || []).map((medico) => [medico.nome.toLowerCase(), medico])
        );
        const registros = (state.documentacao?.registros || []).filter((item) => {
            const nomeCadastro = (item.medico || item.nome || item.valores?.[0] || "").toLowerCase();
            const cadastro = catalogo.get(nomeCadastro);
            if (cadastro?.descredenciado) return false;
            if (categoria === "todos") return true;
            const tipoCadastro = cadastro?.tipo || "credenciado";
            return tipoCadastro === categoria;
        });
        const statusNormalizado = (item) => (item.status || "").trim().toUpperCase();
        const registrosAvaliados = registros.filter((item) => !item.naoIndicado);
        const resumo = {
            total: registrosAvaliados.length,
            conformes: registrosAvaliados.filter((item) => statusNormalizado(item) === "CONFORME").length,
            pendentes: registrosAvaliados.filter((item) => statusNormalizado(item) === "PENDENTE").length,
            notificados: registrosAvaliados.filter((item) => statusNormalizado(item) === "NOTIFICADO").length,
            naoIndicados: registros.length - registrosAvaliados.length,
        };
        const total = resumo.total;
        const percentualStatus = (quantidade) => total
            ? `${((quantidade || 0) / total * 100).toFixed(2).replace(".", ",")}%`
            : "0,00%";
        const percentual = percentualStatus(resumo.conformes);
        const metaIndicador = 75;
        const percentualNumerico = total ? (resumo.conformes / total) * 100 : 0;
        const metaAtingida = percentualNumerico >= metaIndicador;
        el.docsPercentText.innerHTML = `
            <span>Meta do indicador: <strong>${metaIndicador}%</strong></span>
            <span>Resultado geral: <strong>${percentual}</strong></span>
            <span class="docs-goal-status ${metaAtingida ? "is-achieved" : "is-pending"}">
                ${metaAtingida ? "Meta atingida" : "Meta não atingida"}
            </span>
        `;

        const cards = [
            ["Registros", resumo.total || 0, "total"],
            ["CONFORME", resumo.conformes || 0, "conforme"],
            ["PENDENTE", resumo.pendentes || 0, "pendente"],
            ["NOTIFICADO", resumo.notificados || 0, "notificado"],
            ["NÃO INDICADOS", resumo.naoIndicados || 0, "nao-indicado"],
            ["CONFORMES (%)", percentual, "conforme"],
            ["PENDENTES (%)", percentualStatus(resumo.pendentes), "pendente"],
            ["NOTIFICADOS (%)", percentualStatus(resumo.notificados), "notificado"],
        ];

        el.docsSummary.innerHTML = cards.map(([label, value, status]) => `
            <div class="docs-summary-card ${status}">
                <span>${label}</span>
                <strong>${value}</strong>
            </div>
        `).join("");

        renderAvisoVencimentoDocumentos(registros);
    }

    function diasAteVencimento(valor) {
        const [ano, mes, dia] = String(valor || "").split("-").map(Number);
        if (!ano || !mes || !dia) return null;
        const vencimento = Date.UTC(ano, mes - 1, dia);
        const agora = new Date();
        const hoje = Date.UTC(agora.getFullYear(), agora.getMonth(), agora.getDate());
        return Math.ceil((vencimento - hoje) / 86400000);
    }

    function renderAvisoVencimentoDocumentos(registros) {
        const proximos = registros
            .filter((item) => !item.naoIndicado && !item.semValidade)
            .map((item) => ({
                item,
                dias: diasAteVencimento(item.valores?.[2]),
            }))
            .filter(({ dias }) => dias !== null && dias >= 0 && dias <= 60)
            .sort((a, b) => a.dias - b.dias);

        if (!proximos.length) {
            el.docsExpiryAlert.classList.add("hidden");
            el.docsExpiryAlert.innerHTML = "";
            return;
        }

        const itens = proximos.slice(0, 5).map(({ item, dias }) => {
            const nome = item.medico || item.nome || item.valores?.[0] || "Cadastro sem nome";
            const documento = item.documento || item.valores?.[1] || "Documento";
            const prazo = dias === 0 ? "vence hoje" : `vence em ${dias} dia${dias === 1 ? "" : "s"}`;
            return `<li><strong>${escapeHtml(documento)}</strong> — ${escapeHtml(nome)} <span>${prazo}</span></li>`;
        }).join("");
        const restantes = proximos.length - 5;

        el.docsExpiryAlert.innerHTML = `
            <span class="docs-expiry-icon" aria-hidden="true">!</span>
            <div>
                <strong>${proximos.length} documento${proximos.length === 1 ? "" : "s"} próximo${proximos.length === 1 ? "" : "s"} do vencimento</strong>
                <p>Documentos com vencimento previsto para os próximos 60 dias:</p>
                <ul>${itens}</ul>
                ${restantes > 0 ? `<small>Mais ${restantes} documento${restantes === 1 ? "" : "s"} nessa situação.</small>` : ""}
            </div>
        `;
        el.docsExpiryAlert.classList.remove("hidden");
    }

    function renderDocumentacao() {
        renderResumoDocumentacao();
        const medicos = medicosFiltrados();
        const totalDocs = medicos.reduce((total, medico) => total + medico.documentos.length, 0);
        const totalPages = Math.max(1, Math.ceil(medicos.length / state.docsPageSize));
        if (state.docsPage > totalPages) state.docsPage = totalPages;
        if (state.docsPage < 1) state.docsPage = 1;
        const start = (state.docsPage - 1) * state.docsPageSize;
        const medicosPagina = medicos.slice(start, start + state.docsPageSize);

        atualizarContadorAlteracoes();
        el.docsResultCount.textContent = `${medicos.length} cadastro${medicos.length === 1 ? "" : "s"} e ${totalDocs} documento${totalDocs === 1 ? "" : "s"} encontrados.`;
        el.docsPageInfo.textContent = `Página ${state.docsPage} de ${totalPages}`;
        el.docsPrevPage.disabled = state.docsPage <= 1;
        el.docsNextPage.disabled = state.docsPage >= totalPages;
        el.docsPagination.classList.toggle("hidden", medicos.length === 0);

        if (medicos.length === 0) {
            el.docsDoctorsList.innerHTML = `<div class="docs-empty">Nenhum registro encontrado para os filtros atuais.</div>`;
            return;
        }

        el.docsDoctorsList.innerHTML = medicosPagina.map((medico, index) => renderMedicoCard(medico, index)).join("");

        el.docsDoctorsList.querySelectorAll('[contenteditable="true"]').forEach((cell) => {
            cell.addEventListener("input", () => {
                const row = cell.closest(".docs-document-row");
                const id = Number(row.dataset.id);
                const field = cell.dataset.field;
                registrarAlteracaoDocumento(id, { [field]: cell.textContent.trim() }, row);
                agendarSalvamentoDocumento(id);
                if (cell.classList.contains("docs-status-cell")) {
                    cell.className = `docs-status-cell ${normalizarClasseStatus(cell.textContent)}`;
                    cell.dataset.label = cell.textContent.trim() || "-";
                }
            });
            cell.addEventListener("blur", () => {
                const row = cell.closest(".docs-document-row");
                salvarDocumentoAgora(Number(row.dataset.id));
            });
        });

        el.docsDoctorsList.querySelectorAll('input[data-field]').forEach((input) => {
            input.addEventListener("change", () => {
                const row = input.closest(".docs-document-row");
                const id = Number(row.dataset.id);
                const current = {
                    [input.dataset.field]: input.type === "checkbox" ? input.checked : input.value,
                };

                if (input.dataset.field === "semValidade") {
                    const dateInput = row.querySelector('input[data-field="data_vencimento"]');
                    const notificationInput = row.querySelector('input[data-field="data_maxima_notificacao"]');
                    dateInput.disabled = input.checked;
                    if (input.checked) {
                        dateInput.value = "";
                        notificationInput.value = "";
                        current.data_vencimento = "";
                        current.data_maxima_notificacao = "";
                    }
                }

                if (input.dataset.field === "data_vencimento") {
                    const semValidadeInput = row.querySelector('input[data-field="semValidade"]');
                    const notificationInput = row.querySelector('input[data-field="data_maxima_notificacao"]');
                    const semValidadeAutomatica = !input.value;
                    const dataNotificacao = adicionarDiasDataISO(input.value, 60);
                    semValidadeInput.checked = semValidadeAutomatica;
                    notificationInput.value = dataNotificacao;
                    input.disabled = semValidadeAutomatica;
                    current.semValidade = semValidadeAutomatica;
                    current.data_maxima_notificacao = dataNotificacao;
                }

                if (input.dataset.field === "naoIndicado") {
                    row.classList.toggle("is-not-indicated", input.checked);
                }

                registrarAlteracaoDocumento(id, current, row);
                salvarDocumentoAutomaticamente(id);
            });
        });

        el.docsDoctorsList.querySelectorAll(".docs-file-input").forEach((input) => {
            input.addEventListener("change", () => {
                const row = input.closest(".docs-document-row");
                enviarArquivoDocumentacao(Number(row.dataset.id), input);
            });
        });

        el.docsDoctorsList.querySelectorAll('[data-action="toggle-doctor"]').forEach((button) => {
            button.addEventListener("click", () => {
                const card = button.closest(".docs-doctor-card");
                const open = card.classList.toggle("open");
                button.setAttribute("aria-expanded", String(open));
                button.title = open ? "Fechar documentos" : "Abrir documentos";
            });
        });

        el.docsDoctorsList.querySelectorAll('[data-action="add-doc"]').forEach((button) => {
            button.addEventListener("click", () => criarDocumentoParaMedico(button.dataset.medico));
        });

        el.docsDoctorsList.querySelectorAll('[data-action="save-provider-email"]').forEach((button) => {
            button.addEventListener("click", () => salvarEmailMedico(button));
        });

        el.docsDoctorsList.querySelectorAll('[data-action="toggle-provider-notifications"]').forEach((button) => {
            button.addEventListener("click", () => alternarAvisosMedico(button));
        });

        el.docsDoctorsList.querySelectorAll('[data-action="delete-docs"]').forEach((button) => {
            button.addEventListener("click", () => excluirRegistroDocumentacao(Number(button.dataset.id)));
        });

        el.docsDoctorsList.querySelectorAll('[data-action="delete-doctor"]').forEach((button) => {
            button.addEventListener("click", () => {
                const medico = medicosPagina[Number(button.dataset.index)];
                if (medico) excluirMedicoCredenciado(medico);
            });
        });

        el.docsDoctorsList.querySelectorAll('[data-action="toggle-disaccredited"]').forEach((button) => {
            button.addEventListener("click", () => {
                const medico = medicosPagina[Number(button.dataset.index)];
                if (medico) alterarSituacaoCredenciamento(medico);
            });
        });

        el.docsDoctorsList.querySelectorAll('[data-action="choose-status"]').forEach((button) => {
            button.addEventListener("click", () => abrirSeletorStatus(Number(button.dataset.id)));
        });

    }

    function renderMedicoCard(medico, index) {
        const total = medico.documentos.length;
        const firstStatuses = [
            medico.notificados ? `<span class="docs-status-badge notificado">${medico.notificados} notificado${medico.notificados === 1 ? "" : "s"}</span>` : "",
            medico.pendentes ? `<span class="docs-status-badge pendente">${medico.pendentes} pendente${medico.pendentes === 1 ? "" : "s"}</span>` : "",
            medico.conformes ? `<span class="docs-status-badge conforme">${medico.conformes} conforme${medico.conformes === 1 ? "" : "s"}</span>` : "",
            medico.naoIndicados ? `<span class="docs-status-badge nao-indicado">${medico.naoIndicados} não indicado${medico.naoIndicados === 1 ? "" : "s"}</span>` : "",
        ].filter(Boolean).join("");

        return `
            <article class="docs-doctor-card${medico.descredenciado ? " is-disaccredited" : ""}">
                <div class="docs-doctor-head">
                    <div>
                        <h3>${escapeHtml(medico.nome)}</h3>
                        <span class="docs-doctor-type">${DOCTOR_TYPE_LABELS[medico.tipo] || "Méd. credenciado"}</span>
                        <p>${total} documento${total === 1 ? "" : "s"} cadastrado${total === 1 ? "" : "s"}</p>
                        <div class="docs-provider-email">
                            <label for="provider-email-${medico.id}">E-mail para avisos</label>
                            <div>
                                <input id="provider-email-${medico.id}" type="email" maxlength="255" value="${escapeHtml(medico.emailNotificacao || "")}" placeholder="medico@exemplo.com.br">
                                <button class="btn" data-action="save-provider-email" data-id="${medico.id}" type="button">Salvar e-mail</button>
                            </div>
                            <div class="docs-provider-notification-control${medico.receberAvisos ? " is-active" : " is-paused"}">
                                <span>${!medico.emailNotificacao
                                    ? "Cadastre um e-mail para ativar os avisos"
                                    : medico.receberAvisos
                                        ? "Avisos ativos para este cadastro"
                                        : "Avisos pausados para este cadastro"}</span>
                                <button class="docs-provider-notification-button" data-action="toggle-provider-notifications" data-id="${medico.id}" data-enabled="${medico.receberAvisos ? "true" : "false"}" type="button" ${medico.emailNotificacao ? "" : "disabled"}>
                                    ${medico.receberAvisos ? "Pausar" : "Ativar"}
                                </button>
                            </div>
                        </div>
                        ${medico.descredenciado ? `
                            <div class="docs-disaccredit-details">
                                <strong>Motivo:</strong>
                                <span>${escapeHtml(medico.motivoDescredenciamento || "Não informado")}</span>
                                ${medico.arquivoDescredenciamento ? `<a href="${escapeHtml(medico.arquivoDescredenciamento.url)}">Baixar documento do descredenciamento</a>` : ""}
                            </div>
                        ` : ""}
                        <div class="docs-doctor-statuses">${firstStatuses}</div>
                    </div>
                    <div class="docs-doctor-actions">
                        <button class="docs-disaccredit-btn${medico.descredenciado ? " is-restore" : ""}" data-action="toggle-disaccredited" data-index="${index}" type="button">
                            ${medico.descredenciado ? "Recredenciar" : "Descredenciar"}
                        </button>
                        <button class="docs-doctor-delete" data-action="delete-doctor" data-index="${index}" type="button" title="Apagar cadastro e todos os documentos" aria-label="Apagar ${escapeHtml(medico.nome)} e todos os documentos">🗑</button>
                        <button class="docs-doctor-toggle" data-action="toggle-doctor" type="button" title="Abrir documentos" aria-label="Abrir ou fechar documentos" aria-expanded="false">▼</button>
                    </div>
                </div>
                <div class="docs-documents">
                    <div class="docs-expanded-actions">
                        <button class="docs-add-document-btn" data-action="add-doc" data-medico="${escapeHtml(medico.nome)}" type="button">
                            <span aria-hidden="true">+</span>
                            Adicionar documento
                        </button>
                    </div>
                    <div class="docs-documents-head">
                        <span>Documento</span>
                        <span>Vencimento</span>
                        <span>Notificação</span>
                        <span>Status</span>
                        <span>Documentação</span>
                        <span>Ações</span>
                    </div>
                    ${medico.documentos.map((item) => renderDocumentoRow(item, medico.nome)).join("")}
                </div>
            </article>
        `;
    }

    function renderDocumentoRow(item, medicoNome) {
        const valores = item.valores || [];
        const pendente = state.docsAlterados.get(item.id) || {};
        const documento = pendente.documento ?? valores[1] ?? "";
        const dataVencimento = pendente.data_vencimento ?? valores[2] ?? "";
        const dataNotificacao = pendente.data_maxima_notificacao ?? valores[3] ?? "";
        const status = pendente.status ?? valores[4] ?? "";
        const documentacao = pendente.documentacao ?? valores[7] ?? "";
        const semValidade = pendente.semValidade ?? (item.semValidade || !dataVencimento);
        const naoIndicado = pendente.naoIndicado ?? Boolean(item.naoIndicado);
        const arquivo = item.arquivo || null;

        return `
            <div class="docs-document-row${state.docsAlterados.has(item.id) ? " edited" : ""}${naoIndicado ? " is-not-indicated" : ""}" data-id="${item.id}">
                <div class="docs-document-name" contenteditable="true" data-field="documento" spellcheck="false">${escapeHtml(documento)}</div>
                <div class="docs-file-area" data-has-file="${arquivo ? "true" : "false"}">
                    <input class="docs-file-input" id="docsFile${item.id}" type="file">
                    <span class="docs-file-name" title="${arquivo ? escapeHtml(arquivo.nome) : "Nenhum arquivo anexado"}">${arquivo ? escapeHtml(arquivo.nome) : "Nenhum arquivo anexado"}</span>
                    <div class="docs-file-actions">
                        <label class="docs-file-button" for="docsFile${item.id}">${arquivo ? "Substituir" : "Anexar arquivo"}</label>
                        <a class="docs-file-download${arquivo ? "" : " hidden"}" href="${arquivo ? escapeHtml(arquivo.url) : "#"}">Baixar</a>
                    </div>
                </div>
                <div class="docs-date-field">
                    <input type="date" data-field="data_vencimento" value="${escapeHtml(dataVencimento)}" ${semValidade ? "disabled" : ""}>
                    <label><input type="checkbox" data-field="semValidade" ${semValidade ? "checked" : ""}> Sem validade</label>
                </div>
                <input class="docs-date-input" type="date" data-field="data_maxima_notificacao" value="${escapeHtml(dataNotificacao)}">
                <button class="docs-status-cell ${normalizarClasseStatus(status)}" data-action="choose-status" data-id="${item.id}" type="button" title="Clique para alterar o status">${escapeHtml(status || "-")}</button>
                <label class="docs-not-indicated-field">
                    <input type="checkbox" data-field="naoIndicado" ${naoIndicado ? "checked" : ""}>
                    Não indicado
                </label>
                <div class="docs-documentation-field">
                    <div contenteditable="true" data-field="documentacao" spellcheck="false">${escapeHtml(documentacao)}</div>
                </div>
                <div class="docs-action-cell">
                    <button class="docs-delete-btn" data-action="delete-docs" data-id="${item.id}" type="button" title="Apagar documento" aria-label="Apagar documento">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-1 11H8L7 9Zm3 2v7h2v-7h-2Zm4 0v7h2v-7h-2Z"/></svg>
                        <span>Apagar</span>
                    </button>
                </div>
            </div>
        `;
    }

    function normalizarClasseStatus(valor) {
        return (valor || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-");
    }

    function abrirModalMedico() {
        el.doctorForm.reset();
        el.doctorFormError.textContent = "";
        el.doctorFormError.classList.add("hidden");
        el.doctorOverlay.classList.add("open");
        window.setTimeout(() => el.doctorName.focus(), 50);
    }

    function fecharModalMedico() {
        el.doctorOverlay.classList.remove("open");
    }

    async function criarRegistroDocumentacao(event) {
        event.preventDefault();
        const nome = el.doctorName.value.trim();
        const tipo = el.doctorType.value;
        const emailNotificacao = el.doctorEmail.value.trim();
        if (!nome) return;

        try {
            const novo = await requestJson(DOCTORS_API_URL, {
                method: "POST",
                body: JSON.stringify({ nome, tipo, emailNotificacao }),
            });

            fecharModalMedico();
            el.docsCategoryFilter.value = tipo;
            state.docsPage = 1;
            await carregarDocumentacao(true);
            showFeedback("Cadastro adicionado. Abra a seta para incluir documentos.");

            window.setTimeout(() => {
                const medicos = medicosFiltrados();
                const index = medicos.findIndex((item) => item.id === novo.id);
                if (index >= 0) {
                    state.docsPage = Math.floor(index / state.docsPageSize) + 1;
                    renderDocumentacao();
                }
            }, 120);
        } catch (error) {
            el.doctorFormError.textContent = error.message;
            el.doctorFormError.classList.remove("hidden");
            showFeedback(error.message, "error");
        }
    }

    async function salvarEmailMedico(button) {
        const providerId = Number(button.dataset.id);
        const container = button.closest(".docs-provider-email");
        const input = container.querySelector('input[type="email"]');
        const emailNotificacao = input.value.trim();
        const medico = state.documentacao?.medicos?.find((item) => Number(item.id) === providerId);
        const receberAvisos = medico?.emailNotificacao
            ? Boolean(medico.receberAvisos)
            : Boolean(emailNotificacao);
        button.disabled = true;
        button.textContent = "Salvando...";

        try {
            await requestJson(`${DOCTORS_API_URL}/${providerId}`, {
                method: "PATCH",
                body: JSON.stringify({
                    emailNotificacao,
                    receberAvisos: emailNotificacao ? receberAvisos : false,
                }),
            });
            await carregarDocumentacao(true);
            showFeedback(emailNotificacao ? "E-mail de avisos atualizado." : "E-mail de avisos removido.");
        } catch (error) {
            showFeedback(error.message, "error");
            button.disabled = false;
            button.textContent = "Salvar e-mail";
        }
    }

    async function alternarAvisosMedico(button) {
        const providerId = Number(button.dataset.id);
        const medico = state.documentacao?.medicos?.find((item) => Number(item.id) === providerId);
        if (!medico?.emailNotificacao) {
            showFeedback("Cadastre um e-mail antes de ativar os avisos.", "error");
            return;
        }

        const enabled = button.dataset.enabled !== "true";
        button.disabled = true;
        button.textContent = enabled ? "Ativando..." : "Pausando...";

        try {
            await requestJson(`${DOCTORS_API_URL}/${providerId}`, {
                method: "PATCH",
                body: JSON.stringify({
                    emailNotificacao: medico.emailNotificacao,
                    receberAvisos: enabled,
                }),
            });
            await carregarDocumentacao(true);
            showFeedback(enabled
                ? `Avisos ativados para ${medico.nome}.`
                : `Avisos pausados para ${medico.nome}.`);
        } catch (error) {
            button.disabled = false;
            button.textContent = enabled ? "Ativar" : "Pausar";
            showFeedback(error.message, "error");
        }
    }

    async function alterarSituacaoCredenciamento(medico) {
        if (!medico.descredenciado) {
            abrirFormularioDescredenciamento(medico);
            return;
        }

        const confirmar = window.confirm(
            `Deseja recredenciar o cadastro “${medico.nome}”? Nenhum documento será apagado.`
        );
        if (!confirmar) return;

        try {
            await requestJson(`${DOCTORS_API_URL}/${medico.id}`, {
                method: "PATCH",
                body: JSON.stringify({ descredenciado: false }),
            });
            await carregarDocumentacao(true);
            showFeedback("Cadastro recredenciado com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    function abrirFormularioDescredenciamento(medico) {
        state.disaccreditDoctor = medico;
        el.disaccreditForm.reset();
        el.disaccreditDoctorName.textContent = medico.nome;
        el.disaccreditFormError.textContent = "";
        el.disaccreditFormError.classList.add("hidden");
        el.disaccreditOverlay.classList.add("open");
        window.setTimeout(() => el.disaccreditReason.focus(), 50);
    }

    function fecharFormularioDescredenciamento() {
        state.disaccreditDoctor = null;
        el.disaccreditOverlay.classList.remove("open");
        el.disaccreditForm.reset();
    }

    async function salvarDescredenciamento(event) {
        event.preventDefault();
        const medico = state.disaccreditDoctor;
        const motivo = el.disaccreditReason.value.trim();
        if (!medico || !motivo) return;

        const formData = new FormData();
        formData.append("descredenciado", "true");
        formData.append("motivo", motivo);
        const arquivo = el.disaccreditFile.files?.[0];
        if (arquivo) formData.append("arquivo", arquivo);

        try {
            const response = await fetch(`${DOCTORS_API_URL}/${medico.id}`, {
                method: "PATCH",
                headers: { Accept: "application/json" },
                body: formData,
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.erro || "Não foi possível descredenciar o cadastro.");

            fecharFormularioDescredenciamento();
            await carregarDocumentacao(true);
            showFeedback("Cadastro movido para Descredenciados.");
        } catch (error) {
            el.disaccreditFormError.textContent = error.message;
            el.disaccreditFormError.classList.remove("hidden");
        }
    }

    async function criarDocumentoParaMedico(medico) {
        try {
            const novo = await requestJson(DOCS_API_URL, {
                method: "POST",
                body: JSON.stringify({
                    nome_medico: medico,
                    documento: "Novo documento",
                }),
            });

            await carregarDocumentacao(true);
            state.docsPage = Math.max(1, state.docsPage);
            renderDocumentacao();
            showFeedback("Documento adicionado ao médico.");

            window.setTimeout(() => {
                const row = el.docsDoctorsList.querySelector(`[data-id="${novo.id}"]`);
                if (!row) return;
                const card = row.closest(".docs-doctor-card");
                if (card) card.classList.add("open");
                row.scrollIntoView({ behavior: "smooth", block: "center" });
                const firstCell = row.querySelector('[contenteditable="true"]');
                if (firstCell) firstCell.focus();
            }, 120);
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    async function excluirRegistroDocumentacao(id) {
        const confirmar = window.confirm("Deseja apagar este registro da documentação?");
        if (!confirmar) return;

        try {
            await requestJson(`${DOCS_API_URL}/${id}`, { method: "DELETE" });
            state.docsAlterados.delete(id);
            await carregarDocumentacao(true);
            showFeedback("Registro apagado com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    async function excluirMedicoCredenciado(medico) {
        const total = medico.documentos.length;
        const confirmar = window.confirm(
            `Deseja apagar ${medico.nome} e todos os seus ${total} documento${total === 1 ? "" : "s"}?`
        );
        if (!confirmar) return;

        try {
            await requestJson(medico.id ? `${DOCTORS_API_URL}/${medico.id}` : `${DOCS_API_URL}/medico`, {
                method: "DELETE",
                body: JSON.stringify({
                    ids: medico.documentos.map((documento) => documento.id),
                }),
            });
            medico.documentos.forEach((documento) => state.docsAlterados.delete(documento.id));
            await carregarDocumentacao(true);
            showFeedback("Cadastro e documentos apagados com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    function abrirSeletorStatus(id) {
        state.statusEditingId = id;
        el.statusOverlay.classList.add("open");
    }

    function fecharSeletorStatus() {
        state.statusEditingId = null;
        el.statusOverlay.classList.remove("open");
    }

    async function escolherStatusDocumento(status) {
        if (!state.statusEditingId) return;
        const id = state.statusEditingId;
        registrarAlteracaoDocumento(id, { status });
        fecharSeletorStatus();
        await salvarDocumentoAutomaticamente(id);
    }

    function renderCalendar() {
        const cursor = state.calendarCursor;
        el.calMonthLabel.textContent = `${MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`;
        el.calGrid.innerHTML = "";

        DOW.forEach((day) => {
            const cell = document.createElement("div");
            cell.className = "dow";
            cell.textContent = day;
            el.calGrid.appendChild(cell);
        });

        const firstOfMonth = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
        const startWeekday = firstOfMonth.getDay();
        const daysInMonth = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0).getDate();
        const daysInPrevMonth = new Date(cursor.getFullYear(), cursor.getMonth(), 0).getDate();
        const cellsCount = Math.ceil((startWeekday + daysInMonth) / 7) * 7;
        const todayISO = toISODate(new Date());

        for (let i = 0; i < cellsCount; i += 1) {
            const dayNum = i - startWeekday + 1;
            let cellDate;
            let muted = false;

            if (dayNum < 1) {
                cellDate = new Date(cursor.getFullYear(), cursor.getMonth() - 1, daysInPrevMonth + dayNum);
                muted = true;
            } else if (dayNum > daysInMonth) {
                cellDate = new Date(cursor.getFullYear(), cursor.getMonth() + 1, dayNum - daysInMonth);
                muted = true;
            } else {
                cellDate = new Date(cursor.getFullYear(), cursor.getMonth(), dayNum);
            }

            const iso = toISODate(cellDate);
            const cell = document.createElement("button");
            cell.type = "button";
            cell.className = `cal-day selectable${muted ? " muted" : ""}${iso === todayISO ? " today" : ""}${iso === state.selectedDate ? " selected" : ""}`;
            cell.textContent = cellDate.getDate();

            if (state.compromissos.some((item) => item.data === iso && item.status !== "cancelado")) {
                const mark = document.createElement("span");
                mark.className = "mark";
                cell.appendChild(mark);
            }

            cell.addEventListener("click", () => {
                state.selectedDate = iso;
                if (muted) {
                    state.calendarCursor = new Date(cellDate.getFullYear(), cellDate.getMonth(), 1);
                }
                renderCalendar();
                renderDay();
            });

            el.calGrid.appendChild(cell);
        }
    }

    let pickerYear = state.calendarCursor.getFullYear();

    function renderMonthYearPicker() {
        el.myYearLabel.textContent = pickerYear;
        el.myGrid.innerHTML = "";

        MONTHS.forEach((month, index) => {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = month.slice(0, 3);
            if (pickerYear === state.calendarCursor.getFullYear() && index === state.calendarCursor.getMonth()) {
                button.classList.add("current");
            }
            button.addEventListener("click", () => {
                state.calendarCursor = new Date(pickerYear, index, 1);
                renderCalendar();
                closeMonthYearPicker();
            });
            el.myGrid.appendChild(button);
        });
    }

    function openMonthYearPicker() {
        pickerYear = state.calendarCursor.getFullYear();
        renderMonthYearPicker();
        el.myPicker.classList.add("open");
    }

    function closeMonthYearPicker() {
        el.myPicker.classList.remove("open");
    }

    function refreshResponsavelFilter() {
        const responsaveis = Array.from(new Set(state.compromissos.map((item) => item.responsavel).filter(Boolean))).sort();
        const current = el.filterResponsavel.value;
        el.filterResponsavel.innerHTML = '<option value="">Todos</option>' + responsaveis.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("");
        el.filterResponsavel.value = responsaveis.includes(current) ? current : "";
        el.respList.innerHTML = responsaveis.map((item) => `<option value="${escapeHtml(item)}">`).join("");
    }

    function compromissoFiltrado(item) {
        const searchTerm = el.searchInput.value.trim().toLowerCase();
        const responsavel = el.filterResponsavel.value;
        const status = el.filterStatus.value;

        if (item.data !== state.selectedDate) return false;
        if (responsavel && item.responsavel !== responsavel) return false;
        if (status && item.status !== status) return false;
        if (!searchTerm) return true;

        return [item.titulo, item.descricao, item.local, item.responsavel]
            .some((value) => (value || "").toLowerCase().includes(searchTerm));
    }

    function renderDay() {
        const dateObj = parseISODate(state.selectedDate);
        el.selectedDateTitle.textContent = `${WEEKDAY_FULL[dateObj.getDay()]}, ${dateObj.getDate()} de ${MONTHS[dateObj.getMonth()].toLowerCase()}`;
        el.selectedDateSub.textContent = String(dateObj.getFullYear());

        const items = state.compromissos
            .filter(compromissoFiltrado)
            .sort((a, b) => (a.horaInicio || "").localeCompare(b.horaInicio || ""));

        el.daySummary.textContent = items.length === 0
            ? "Nenhum compromisso encontrado para os filtros atuais."
            : `${items.length} compromisso${items.length > 1 ? "s" : ""} nesta data.`;

        el.apptList.innerHTML = "";

        if (items.length === 0) {
            el.apptList.innerHTML = `
                <div class="empty-state">
                    <h3>Nada agendado neste dia</h3>
                    <p>Use o botão Novo compromisso para incluir um horário.</p>
                    <button class="btn btn-primary" id="emptyAddBtn" type="button">Novo compromisso</button>
                </div>
            `;
            document.getElementById("emptyAddBtn").addEventListener("click", () => openModal());
            return;
        }

        items.forEach((item) => {
            const card = document.createElement("article");
            card.className = "appointment-card";
            const descricao = item.descricao || "";
            const descricaoLonga = descricao.length > 180;
            const descricaoResumo = descricaoLonga ? `${descricao.slice(0, 180).trim()}...` : descricao;

            const statusOptions = Object.entries(STATUS_LABELS)
                .map(([status, label]) => `<option value="${status}" ${status === item.status ? "selected" : ""}>${label}</option>`)
                .join("");

            card.innerHTML = `
                <div class="time-box">
                    <strong>${escapeHtml(item.horaInicio || "--:--")}</strong>
                    <span>${item.horaFim ? `até ${escapeHtml(item.horaFim)}` : "sem fim"}</span>
                </div>
                <div class="appointment-body">
                    <h3>${escapeHtml(item.titulo)}</h3>
                    <div class="appointment-meta">
                        ${item.responsavel ? `<span>Responsável: ${escapeHtml(item.responsavel)}</span>` : ""}
                        ${item.local ? `<span>Local: ${escapeHtml(item.local)}</span>` : ""}
                    </div>
                    ${descricao ? `
                        <div class="appointment-desc-wrap">
                            <p class="appointment-desc" data-full="${escapeHtml(descricao)}" data-short="${escapeHtml(descricaoResumo)}">${escapeHtml(descricaoResumo)}</p>
                            ${descricaoLonga ? `<button class="desc-toggle" data-action="toggle-desc" type="button">Ver mais</button>` : ""}
                        </div>
                    ` : ""}
                </div>
                <div class="appointment-actions">
                    <select class="appointment-status-select stamp ${escapeHtml(item.status)}" data-action="status-select" data-id="${item.id}" aria-label="Alterar status do compromisso">
                        ${statusOptions}
                    </select>
                    <div class="appointment-direct-actions">
                        <button class="icon-btn" data-action="edit" data-id="${item.id}" type="button">Editar</button>
                        <button class="icon-btn danger-text" data-action="delete" data-id="${item.id}" type="button">Excluir</button>
                    </div>
                </div>
            `;
            el.apptList.appendChild(card);
        });

        el.apptList.querySelectorAll('[data-action="toggle-desc"]').forEach((button) => {
            button.addEventListener("click", () => {
                const wrapper = button.closest(".appointment-desc-wrap");
                const description = wrapper.querySelector(".appointment-desc");
                const expanded = wrapper.classList.toggle("expanded");

                description.textContent = expanded ? description.dataset.full : description.dataset.short;
                button.textContent = expanded ? "Ver menos" : "Ver mais";
            });
        });

        el.apptList.querySelectorAll('[data-action="edit"]').forEach((button) => {
            button.addEventListener("click", () => openModal(Number(button.dataset.id)));
        });

        el.apptList.querySelectorAll('[data-action="delete"]').forEach((button) => {
            button.addEventListener("click", () => {
                state.deletingId = Number(button.dataset.id);
                el.confirmOverlay.classList.add("open");
            });
        });

        el.apptList.querySelectorAll('[data-action="status-select"]').forEach((select) => {
            select.addEventListener("change", () => alterarStatus(Number(select.dataset.id), select.value));
        });
    }

    function openModal(id) {
        el.apptForm.reset();
        limparErroCompromisso();
        el.fData.value = state.selectedDate;
        el.fStatus.value = "agendado";
        el.fHoraFim.dataset.manual = "false";

        if (id) {
            const item = state.compromissos.find((compromisso) => compromisso.id === id);
            if (!item) return;

            el.modalTitle.textContent = "Editar compromisso";
            el.apptId.value = item.id;
            el.fTitulo.value = item.titulo || "";
            el.fData.value = item.data || state.selectedDate;
            el.fHoraInicio.value = item.horaInicio || "";
            el.fHoraFim.value = item.horaFim || "";
            el.fHoraFim.dataset.manual = item.horaFim ? "true" : "false";
            el.fResponsavel.value = item.responsavel || "";
            el.fLocal.value = item.local || "";
            el.fStatus.value = item.status || "agendado";
            el.fDescricao.value = item.descricao || "";
        } else {
            el.modalTitle.textContent = "Novo compromisso";
            el.apptId.value = "";
        }

        el.modalOverlay.classList.add("open");
        window.setTimeout(() => el.fTitulo.focus(), 50);
    }

    function closeModal() {
        limparErroCompromisso();
        el.modalOverlay.classList.remove("open");
    }

    function formPayload() {
        return {
            titulo: el.fTitulo.value.trim(),
            data: el.fData.value,
            horaInicio: el.fHoraInicio.value,
            horaFim: el.fHoraFim.value,
            responsavel: el.fResponsavel.value.trim(),
            local: el.fLocal.value.trim(),
            status: el.fStatus.value,
            descricao: el.fDescricao.value.trim(),
        };
    }

    function horaMaisUmaHora(hora) {
        if (!hora) return "";

        const [hours, minutes] = hora.split(":").map(Number);
        const date = new Date(2000, 0, 1, hours, minutes);
        date.setHours(date.getHours() + 1);
        return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    }

    function preencherHoraFimAutomatica() {
        if (!el.fHoraInicio.value) return;
        if (el.fHoraFim.dataset.manual === "true" && el.fHoraFim.value) return;

        el.fHoraFim.value = horaMaisUmaHora(el.fHoraInicio.value);
        el.fHoraFim.dataset.manual = "false";
    }

    async function salvarCompromisso(event) {
        event.preventDefault();
        const id = el.apptId.value;
        const payload = formPayload();

        try {
            const item = await requestJson(id ? `${API_URL}/${id}` : API_URL, {
                method: id ? "PUT" : "POST",
                body: JSON.stringify(payload),
            });

            state.selectedDate = item.data;
            state.calendarCursor = new Date(parseISODate(item.data).getFullYear(), parseISODate(item.data).getMonth(), 1);
            closeModal();
            await carregarCompromissos();
            showFeedback("Compromisso salvo com sucesso.");
        } catch (error) {
            mostrarErroCompromisso(error.message);
        }
    }

    async function excluirCompromisso() {
        if (!state.deletingId) return;

        try {
            await requestJson(`${API_URL}/${state.deletingId}`, { method: "DELETE" });
            state.deletingId = null;
            el.confirmOverlay.classList.remove("open");
            await carregarCompromissos();
            showFeedback("Compromisso excluído com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    async function alterarStatus(id, status) {
        try {
            await requestJson(`${API_URL}/${id}/status`, {
                method: "PATCH",
                body: JSON.stringify({ status }),
            });
            await carregarCompromissos();
            showFeedback("Status atualizado com sucesso.");
        } catch (error) {
            showFeedback(error.message, "error");
        }
    }

    function bindEvents() {
        el.agendaTabs.forEach((tab) => {
            tab.addEventListener("click", () => switchView(tab.dataset.view));
        });
        if (el.evaluationNewTrigger && el.evaluationNewOverlay) {
            el.evaluationNewTrigger.addEventListener("click", openEvaluationModal);
            el.evaluationModalCloseButtons.forEach((button) => {
                button.addEventListener("click", closeEvaluationModal);
            });
            el.evaluationProviderSelect.addEventListener("change", () => {
                el.evaluationStartButton.disabled = !el.evaluationProviderSelect.value;
                setEvaluationMessage(el.evaluationNewError);
            });
            el.evaluationStartButton.addEventListener("click", iniciarAvaliacao);
            el.evaluationProcessItems.addEventListener("click", (event) => {
                const button = event.target.closest("[data-evaluation-open]");
                if (button) abrirAvaliacao(Number(button.dataset.evaluationOpen));
            });
            el.evaluationTermFile.addEventListener("change", () => {
                el.evaluationTermFileName.textContent = el.evaluationTermFile.files?.[0]?.name || state.termoAdesao?.arquivo?.nome || "Nenhum arquivo selecionado";
                setEvaluationMessage(el.evaluationTermMessage);
            });
            el.evaluationTermPositions.forEach((input) => input.addEventListener("change", () => setEvaluationMessage(el.evaluationTermMessage)));
            el.evaluationTermSaveButton.addEventListener("click", salvarTermoAdesao);
        }
        document.querySelectorAll('[data-action="open-minutes-form"]').forEach((button) => {
            button.addEventListener("click", abrirFormularioAta);
        });
        el.cancelMinutesBtn.addEventListener("click", fecharFormularioAta);
        el.secondaryCancelMinutesBtn.addEventListener("click", fecharFormularioAta);
        el.minutesOverlay.addEventListener("click", (event) => {
            if (event.target === el.minutesOverlay) fecharFormularioAta();
        });
        el.minutesFile.addEventListener("change", () => {
            el.minutesFileName.textContent = el.minutesFile.files?.[0]?.name || "PDF, DOC ou DOCX";
        });
        el.minutesForm.addEventListener("submit", salvarAta);
        el.minutesSearch.addEventListener("input", renderAtas);
        el.minutesYearFilter.addEventListener("change", renderAtas);
        el.minutesTypeFilter.addEventListener("change", renderAtas);
        el.minutesOrder.addEventListener("change", renderAtas);
        el.themeToggle.addEventListener("click", toggleTheme);
        el.printBtn.addEventListener("click", () => window.print());
        el.exportMonthPdfBtn.addEventListener("click", () => {
            const ano = state.calendarCursor.getFullYear();
            const mes = state.calendarCursor.getMonth() + 1;
            window.location.href = `/agenda/pdf?ano=${ano}&mes=${mes}`;
        });
        el.newApptBtn.addEventListener("click", () => openModal());
        el.prevMonth.addEventListener("click", () => {
            state.calendarCursor = new Date(state.calendarCursor.getFullYear(), state.calendarCursor.getMonth() - 1, 1);
            renderCalendar();
        });
        el.nextMonth.addEventListener("click", () => {
            state.calendarCursor = new Date(state.calendarCursor.getFullYear(), state.calendarCursor.getMonth() + 1, 1);
            renderCalendar();
        });
        el.calMonthLabel.addEventListener("click", () => {
            if (el.myPicker.classList.contains("open")) closeMonthYearPicker();
            else openMonthYearPicker();
        });
        el.myPrevYear.addEventListener("click", () => {
            pickerYear -= 1;
            renderMonthYearPicker();
        });
        el.myNextYear.addEventListener("click", () => {
            pickerYear += 1;
            renderMonthYearPicker();
        });
        el.filterResponsavel.addEventListener("change", renderDay);
        el.filterStatus.addEventListener("change", renderDay);
        el.searchInput.addEventListener("input", renderDay);
        el.fHoraInicio.addEventListener("change", preencherHoraFimAutomatica);
        el.fHoraFim.addEventListener("input", () => {
            el.fHoraFim.dataset.manual = el.fHoraFim.value ? "true" : "false";
        });
        el.cancelModalBtn.addEventListener("click", closeModal);
        el.secondaryCancelModalBtn.addEventListener("click", closeModal);
        el.modalOverlay.addEventListener("click", (event) => {
            if (event.target === el.modalOverlay) closeModal();
        });
        el.apptForm.addEventListener("submit", salvarCompromisso);
        el.apptForm.addEventListener("input", limparErroCompromisso);
        el.cancelDeleteBtn.addEventListener("click", () => {
            state.deletingId = null;
            el.confirmOverlay.classList.remove("open");
        });
        el.confirmDeleteBtn.addEventListener("click", excluirCompromisso);
        el.cancelStatusBtn.addEventListener("click", fecharSeletorStatus);
        el.statusOverlay.querySelectorAll("[data-status-option]").forEach((button) => {
            button.addEventListener("click", () => escolherStatusDocumento(button.dataset.statusOption));
        });
        if (el.docsEmailGlobalButton) {
            el.docsEmailGlobalButton.addEventListener("click", alternarAvisosGlobais);
        }
        el.newDocsBtn.addEventListener("click", abrirModalMedico);
        el.doctorForm.addEventListener("submit", criarRegistroDocumentacao);
        el.doctorName.addEventListener("input", () => {
            el.doctorFormError.textContent = "";
            el.doctorFormError.classList.add("hidden");
        });
        el.cancelDoctorBtn.addEventListener("click", fecharModalMedico);
        el.secondaryCancelDoctorBtn.addEventListener("click", fecharModalMedico);
        el.doctorOverlay.addEventListener("click", (event) => {
            if (event.target === el.doctorOverlay) fecharModalMedico();
        });
        el.disaccreditForm.addEventListener("submit", salvarDescredenciamento);
        el.cancelDisaccreditBtn.addEventListener("click", fecharFormularioDescredenciamento);
        el.secondaryCancelDisaccreditBtn.addEventListener("click", fecharFormularioDescredenciamento);
        el.disaccreditOverlay.addEventListener("click", (event) => {
            if (event.target === el.disaccreditOverlay) fecharFormularioDescredenciamento();
        });
        window.addEventListener("online", tentarSalvarDocumentosPendentes);
        window.addEventListener("beforeunload", (event) => {
            if (
                state.docsAlterados.size > 0 ||
                state.docsSalvando.size > 0 ||
                state.docsSaveTimers.size > 0
            ) {
                event.preventDefault();
                event.returnValue = "";
            }
        });
        el.docsPrevPage.addEventListener("click", () => {
            state.docsPage -= 1;
            renderDocumentacao();
        });
        el.docsNextPage.addEventListener("click", () => {
            state.docsPage += 1;
            renderDocumentacao();
        });
        el.docsStatusFilter.addEventListener("change", () => {
            state.docsPage = 1;
            renderDocumentacao();
        });
        el.docsCategoryFilter.addEventListener("change", () => {
            state.docsPage = 1;
            renderDocumentacao();
        });
        el.docsSearchInput.addEventListener("input", () => {
            state.docsPage = 1;
            renderDocumentacao();
        });
        el.confirmOverlay.addEventListener("click", (event) => {
            if (event.target === el.confirmOverlay) el.confirmOverlay.classList.remove("open");
        });
        el.statusOverlay.addEventListener("click", (event) => {
            if (event.target === el.statusOverlay) fecharSeletorStatus();
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeModal();
                closeMonthYearPicker();
                el.confirmOverlay.classList.remove("open");
                fecharSeletorStatus();
                fecharModalMedico();
                fecharFormularioDescredenciamento();
                fecharFormularioAta();
                closeEvaluationModal();
            }
        });
        document.addEventListener("click", (event) => {
            if (!el.myPicker.contains(event.target) && event.target !== el.calMonthLabel) {
                closeMonthYearPicker();
            }
        });
    }

    function init() {
        initTheme();
        bindEvents();
        carregarCompromissos();
        if (el.documentacaoView?.classList.contains("active")) {
            carregarEstadoAvisosGlobais();
        }
    }

    init();
})();
