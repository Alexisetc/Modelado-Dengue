const rawAuditData = document.getElementById("audit-data").textContent;
        // #region agent log
        fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H1',location:'generate_migration_audit.py:1356',message:'audit-data recibido',data:{length:rawAuditData.length,startsWith:rawAuditData.slice(0,80)},timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        let audit;
        try {
            audit = JSON.parse(rawAuditData);
            // #region agent log
            fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H1',location:'generate_migration_audit.py:1361',message:'JSON parse correcto',data:{entryCount:audit?.entries?.length ?? null,summaryKeys:Object.keys(audit?.summary || {})},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
        } catch (error) {
            // #region agent log
            fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H1',location:'generate_migration_audit.py:1365',message:'Fallo JSON.parse',data:{name:error?.name,message:error?.message},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
            throw error;
        }
        const summary = audit.summary;
        const allEntries = audit.entries;
        let activeTab = "resumen";
        let currentEntryId = allEntries[0]?.id || null;
        let currentFilter = "all";
        let currentSearch = "";

        function switchTab(tab) {
            activeTab = tab;
            document.getElementById("view-resumen").classList.toggle("hidden", tab !== "resumen");
            document.getElementById("view-diff").classList.toggle("hidden", tab !== "diff");
            document.getElementById("tab-resumen").className = tab === "resumen"
                ? "tab-active py-3 flex items-center gap-2"
                : "tab-inactive py-3 flex items-center gap-2";
            document.getElementById("tab-diff").className = tab === "diff"
                ? "tab-active py-3 flex items-center gap-2"
                : "tab-inactive py-3 flex items-center gap-2";
            if (tab === "diff") {
                renderDiff(currentEntryId);
            }
        }

        function initHeader() {
            document.getElementById("generated-at").textContent = summary.generatedAt;
            document.getElementById("regen-command").textContent = summary.regenerateCommand;
        }

        function renderSummary() {
            const cards = [
                ["Archivos MATLAB", summary.matlabCount, "file-code-2", "text-red-600 bg-red-50"],
                ["Modulos Python", summary.pythonCount, "file-json-2", "text-blue-600 bg-blue-50"],
                ["Pares 1:1", summary.pairedCount, "git-branch-plus", "text-emerald-600 bg-emerald-50"],
                ["Modulos nuevos Python", summary.pythonOnlyCount, "package-plus", "text-amber-600 bg-amber-50"],
                ["Cobertura", summary.coveragePercent + "%", "badge-check", "text-teal-700 bg-teal-50"],
            ];

            document.getElementById("summary-cards").innerHTML = cards.map(([label, value, icon, styles]) => `
                <article class="summary-card glass-panel border border-white/80 rounded-[24px] p-5 shadow-lg">
                    <div class="flex items-start justify-between gap-4">
                        <div>
                            <div class="text-xs uppercase tracking-[0.18em] text-slate-500">${label}</div>
                            <div class="text-3xl font-bold text-slate-900 mt-3">${value}</div>
                            <div class="text-sm text-slate-500 mt-2">Estado actual leido desde los archivos conectados al reporte.</div>
                        </div>
                        <div class="w-12 h-12 rounded-2xl flex items-center justify-center ${styles}">
                            <i data-lucide="${icon}" class="w-6 h-6"></i>
                        </div>
                    </div>
                </article>
            `).join("");

            document.getElementById("methodology-text").textContent = summary.methodology;
            document.getElementById("quick-facts").innerHTML = [
                `El reporte compara ${summary.pairedCount} pares reales MATLAB/Python usando el contenido actual del disco.`,
                `Hay ${summary.pythonOnlyCount} modulos nuevos de soporte en Python que no existian como archivo MATLAB.`,
                `El total agregado por la migracion auditada es de ${summary.totalAddedLines} lineas y el total removido es de ${summary.totalRemovedLines}.`,
                summary.mostChangedStem ? `El archivo con mayor volumen de cambios es ${summary.mostChangedStem}.` : "No se detectaron cambios significativos."
            ].map(text => `
                <li class="rounded-2xl border border-slate-200 bg-white px-4 py-3 leading-6 shadow-sm">
                    ${escapeHtml(text)}
                </li>
            `).join("");
        }

        function kindBadge(kind) {
            if (kind === "paired") return "kind-paired";
            if (kind === "python-only") return "kind-python-only";
            return "kind-matlab-only";
        }

        function renderTransformationTable() {
            const tbody = document.getElementById("transformation-table");
            // #region agent log
            fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H3',location:'generate_migration_audit.py:1430',message:'Entrando a renderTransformationTable',data:{entryCount:allEntries.length,firstEntryId:allEntries[0]?.id ?? null,hasAlerts:Array.isArray(allEntries[0]?.detail?.alerts)},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
            tbody.innerHTML = allEntries.map(entry => `
                <tr class="hover:bg-slate-50/70">
                    <td class="px-3 py-3">
                        <div class="mono text-sm text-rose-700 font-medium">${escapeHtml(entry.matlabName)}</div>
                        <div class="text-xs text-slate-500 mt-1">${escapeHtml(entry.matlabRelPath || "Sin archivo MATLAB asociado")}</div>
                    </td>
                    <td class="px-3 py-3">
                        <div class="mono text-sm text-emerald-700 font-medium">${escapeHtml(entry.pythonName)}</div>
                        <div class="text-xs text-slate-500 mt-1">${escapeHtml(entry.pythonRelPath || "Sin archivo Python asociado")}</div>
                    </td>
                    <td class="px-3 py-3">
                        <span class="inline-flex px-2.5 py-1 rounded-full border text-[11px] font-semibold whitespace-nowrap ${kindBadge(entry.kind)}">
                            ${escapeHtml(entry.statusLabel)}
                        </span>
                    </td>
                    <td class="px-3 py-3 text-slate-700 min-w-[130px]">${escapeHtml(entry.category)}</td>
                    <td class="px-3 py-3 text-slate-700 leading-6 min-w-[250px] max-w-[320px]">${escapeHtml(entry.purpose)}</td>
                    <td class="px-3 py-3 text-slate-600 leading-6 min-w-[250px] max-w-[320px]">${escapeHtml(entry.transform)}</td>
                    <td class="px-3 py-3 min-w-[220px] w-[220px]">
                        <div class="flex flex-col gap-2">
                            ${entry.detail.alerts.length ? `
                                <div class="alert-chip w-full">
                                    <i data-lucide="triangle-alert" class="w-3.5 h-3.5"></i>
                                    ${entry.detail.alerts.length} alerta${entry.detail.alerts.length === 1 ? "" : "s"}
                                </div>
                            ` : ""}
                            <button class="inline-flex items-center justify-center gap-2 text-sm px-3 py-1.5 rounded-xl bg-blue-600 text-white hover:bg-blue-500 whitespace-nowrap w-full" onclick="openInspector('${entry.id}')">
                                <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                                Abrir diff
                            </button>
                            <button class="inline-flex items-center justify-center gap-2 text-sm px-3 py-1.5 rounded-xl border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 whitespace-nowrap w-full" onclick="openDetailModal('${entry.id}')">
                                <i data-lucide="book-open-text" class="w-4 h-4"></i>
                                Conocer más
                            </button>
                        </div>
                    </td>
                </tr>
            `).join("");
            lucide.createIcons();
        }

        function renderList(items, elementId) {
            document.getElementById(elementId).innerHTML = items
                .map(item => `<li>${escapeHtml(item)}</li>`)
                .join("");
        }

        function renderAlerts(alerts, elementId) {
            const container = document.getElementById(elementId);
            if (!alerts.length) {
                container.innerHTML = `
                    <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                        No se detectaron parametros pegados, curvas embebidas ni umbrales fijos con las reglas actuales de la auditoria.
                    </div>
                `;
                return;
            }
            container.innerHTML = alerts.map(alert => `
                <article class="alert-card ${alert.level === "info" ? "alert-card-info" : ""}">
                    <div class="flex items-center gap-2">
                        <span class="alert-chip">
                            <i data-lucide="${alert.level === "info" ? "info" : "triangle-alert"}" class="w-3.5 h-3.5"></i>
                            ${alert.level === "info" ? "Revision" : "Alerta"}
                        </span>
                        <h4 class="text-sm font-semibold text-slate-900">${escapeHtml(alert.title)}</h4>
                    </div>
                    <p class="mt-3 text-sm text-slate-700 leading-6">${escapeHtml(alert.message)}</p>
                    ${alert.evidence.length ? `
                        <div class="mt-3">
                            <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-2">Evidencia encontrada</div>
                            <pre class="alert-evidence mono">${escapeHtml(alert.evidence.join("\n"))}</pre>
                        </div>
                    ` : ""}
                </article>
            `).join("");
        }

        function openDetailModal(id) {
            const entry = allEntries.find(item => item.id === id);
            if (!entry) return;

            document.getElementById("modal-status").textContent = entry.statusLabel;
            document.getElementById("modal-status").className = `pill-badge ${kindBadge(entry.kind)}`;
            document.getElementById("modal-category").textContent = entry.category;
            document.getElementById("modal-title").textContent = `${entry.matlabName} → ${entry.pythonName}`;
            document.getElementById("modal-overview").textContent = entry.detail.overview;
            renderList(entry.detail.inputs, "modal-inputs");
            renderList(entry.detail.outputs, "modal-outputs");
            renderList(entry.detail.dependencies, "modal-dependencies");
            renderList(entry.detail.flow, "modal-flow");
            renderList(entry.detail.migrationNotes, "modal-migration-notes");
            renderAlerts(entry.detail.alerts || [], "modal-alerts");
            document.getElementById("modal-code-explanation").textContent = entry.detail.codeExplanation;
            document.getElementById("modal-python-label").textContent = entry.pythonRelPath || "Sin archivo Python";
            document.getElementById("modal-matlab-label").textContent = entry.matlabRelPath || "Sin archivo MATLAB";
            document.getElementById("modal-python-code").textContent = entry.detail.pythonSnippet || "Sin snippet Python disponible.";
            document.getElementById("modal-matlab-code").textContent = entry.detail.matlabSnippet || "Sin snippet MATLAB disponible.";
            document.getElementById("file-detail-modal").classList.remove("hidden");
            document.body.classList.add("overflow-hidden");
            lucide.createIcons();
        }

        function closeDetailModal() {
            document.getElementById("file-detail-modal").classList.add("hidden");
            document.body.classList.remove("overflow-hidden");
        }

        function buildFilters() {
            const filters = [
                ["all", "Todos"],
                ["paired", "Migrados 1:1"],
                ["python-only", "Nuevos en Python"],
                ["matlab-only", "Solo MATLAB"],
            ];
            document.getElementById("kind-filters").innerHTML = filters.map(([value, label]) => `
                <button onclick="setFilter('${value}')" class="px-3 py-1.5 rounded-full border text-xs font-semibold ${currentFilter === value ? "filter-active" : "filter-idle"}">
                    ${label}
                </button>
            `).join("");
        }

        function filteredEntries() {
            return allEntries.filter(entry => {
                const matchesKind = currentFilter === "all" ? true : entry.kind === currentFilter;
                const haystack = `${entry.id} ${entry.matlabName} ${entry.pythonName} ${entry.category} ${entry.purpose}`.toLowerCase();
                const matchesSearch = haystack.includes(currentSearch.toLowerCase());
                return matchesKind && matchesSearch;
            });
        }

        function navButtonClass(disabled) {
            return disabled
                ? "nav-button-disabled rounded-xl px-3 py-2.5"
                : "nav-button rounded-xl px-3 py-2.5";
        }

        function renderInspectorPicker() {
            const entries = filteredEntries();
            if (!entries.some(entry => entry.id === currentEntryId) && entries.length) {
                currentEntryId = entries[0].id;
            }

            const entrySelect = document.getElementById("entry-select");
            const resultCount = document.getElementById("search-result-count");
            const pickerPosition = document.getElementById("picker-position");
            const pickerPositionInline = document.getElementById("picker-position-inline");
            const prevButton = document.getElementById("prev-entry");
            const nextButton = document.getElementById("next-entry");

            resultCount.textContent = `${entries.length} archivo${entries.length === 1 ? "" : "s"}`;

            if (!entries.length) {
                currentEntryId = null;
                entrySelect.innerHTML = '<option value="">Sin coincidencias</option>';
                pickerPosition.textContent = "Archivo 0 de 0";
                pickerPositionInline.textContent = "Archivo 0 de 0";
                prevButton.disabled = true;
                nextButton.disabled = true;
                prevButton.className = navButtonClass(true);
                nextButton.className = navButtonClass(true);
                document.getElementById("diff-output").innerHTML = '<div class="p-6 text-sm text-slate-500">Ajusta la búsqueda o el filtro para volver a cargar un diff.</div>';
                return;
            }

            entrySelect.innerHTML = entries.map(entry => `
                <option value="${escapeHtml(entry.id)}">${escapeHtml(entry.pythonName)} · ${escapeHtml(entry.category)} · ${escapeHtml(entry.statusLabel)}</option>
            `).join("");
            entrySelect.value = currentEntryId;

            const currentIndex = Math.max(entries.findIndex(entry => entry.id === currentEntryId), 0);
            pickerPosition.textContent = `Archivo ${currentIndex + 1} de ${entries.length}`;
            pickerPositionInline.textContent = `Archivo ${currentIndex + 1} de ${entries.length}`;

            prevButton.disabled = currentIndex <= 0;
            nextButton.disabled = currentIndex >= entries.length - 1;
            prevButton.className = navButtonClass(prevButton.disabled);
            nextButton.className = navButtonClass(nextButton.disabled);
            lucide.createIcons();
            renderDiff(currentEntryId);
        }

        function setFilter(value) {
            currentFilter = value;
            buildFilters();
            renderInspectorPicker();
        }

        function openInspector(id) {
            currentEntryId = id;
            switchTab("diff");
            buildFilters();
            renderInspectorPicker();
        }

        function selectEntry(id) {
            currentEntryId = id;
            renderInspectorPicker();
        }

        function moveEntry(step) {
            const entries = filteredEntries();
            const index = entries.findIndex(entry => entry.id === currentEntryId);
            if (index === -1) return;
            const nextEntry = entries[index + step];
            if (!nextEntry) return;
            currentEntryId = nextEntry.id;
            renderInspectorPicker();
        }

        function statCard(label, value) {
            return `
                <span class="mini-stat">${label}<strong>${value}</strong></span>
            `;
        }

        function formatCode(code) {
            if (!code) {
                return '<span class="diff-empty-note">(sin contenido)</span>';
            }
            return escapeHtml(code);
        }

        function buildStructuredPatch(entry) {
            const beforeName = entry.matlabRelPath || "Sin archivo MATLAB";
            const afterName = entry.pythonRelPath || "Sin archivo Python";
            return Diff.structuredPatch(
                beforeName,
                afterName,
                entry.matlabCode || "",
                entry.pythonCode || "",
                "Original MATLAB",
                "Estado Python",
                { context: 100000 }
            );
        }

        function buildUnifiedRows(entry) {
            const patch = buildStructuredPatch(entry);
            let oldLine = 1;
            let newLine = 1;
            let rows = "";

            if (!patch.hunks.length) {
                return `<div class="p-6 text-sm text-slate-500">No hay diferencias detectadas entre los archivos seleccionados.</div>`;
            }

            patch.hunks.forEach((hunk) => {
                rows += `<tr class="diff-separator"><td colspan="3">${escapeHtml(hunk.oldStart + "," + hunk.oldLines + " -> " + hunk.newStart + "," + hunk.newLines)}</td></tr>`;
                hunk.lines.forEach((line) => {
                    const marker = line[0];
                    const content = line.slice(1);
                    if (marker === "\\") {
                        return;
                    }

                    if (marker === " ") {
                        rows += `
                            <tr class="diff-row-context">
                                <td class="diff-num">${oldLine}</td>
                                <td class="diff-num">${newLine}</td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        oldLine += 1;
                        newLine += 1;
                    } else if (marker === "-") {
                        rows += `
                            <tr class="diff-row-removed">
                                <td class="diff-num">${oldLine}</td>
                                <td class="diff-num"></td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        oldLine += 1;
                    } else if (marker === "+") {
                        rows += `
                            <tr class="diff-row-added">
                                <td class="diff-num"></td>
                                <td class="diff-num">${newLine}</td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        newLine += 1;
                    }
                });
            });

            return `
                <table class="diff-table">
                    <thead>
                        <tr>
                            <th class="diff-num">MATLAB</th>
                            <th class="diff-num">Python</th>
                            <th class="text-left px-3 py-2">Codigo</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        function renderSideBySideHunk(hunk, state) {
            let rows = "";
            let index = 0;
            while (index < hunk.lines.length) {
                const line = hunk.lines[index];
                const marker = line[0];
                if (marker === "\\") {
                    index += 1;
                    continue;
                }

                if (marker === " ") {
                    const content = line.slice(1);
                    rows += `
                        <tr>
                            <td class="diff-num">${state.oldLine}</td>
                            <td class="diff-code-cell diff-row-context"><pre class="diff-code">${formatCode(content)}</pre></td>
                            <td class="diff-num">${state.newLine}</td>
                            <td class="diff-code-cell diff-row-context"><pre class="diff-code">${formatCode(content)}</pre></td>
                        </tr>
                    `;
                    state.oldLine += 1;
                    state.newLine += 1;
                    index += 1;
                    continue;
                }

                if (marker === "-") {
                    const removed = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "-") {
                        removed.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    const added = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "+") {
                        added.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    const total = Math.max(removed.length, added.length);
                    for (let offset = 0; offset < total; offset += 1) {
                        const left = removed[offset];
                        const right = added[offset];
                        const leftNumber = left !== undefined ? state.oldLine++ : "";
                        const rightNumber = right !== undefined ? state.newLine++ : "";
                        rows += `
                            <tr>
                                <td class="diff-num">${leftNumber}</td>
                                <td class="diff-code-cell ${left !== undefined ? "diff-row-removed" : "diff-row-empty"}"><pre class="diff-code">${formatCode(left || "")}</pre></td>
                                <td class="diff-num">${rightNumber}</td>
                                <td class="diff-code-cell ${right !== undefined ? "diff-row-added" : "diff-row-empty"}"><pre class="diff-code">${formatCode(right || "")}</pre></td>
                            </tr>
                        `;
                    }
                    continue;
                }

                if (marker === "+") {
                    const added = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "+") {
                        added.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    added.forEach((content) => {
                        rows += `
                            <tr>
                                <td class="diff-num"></td>
                                <td class="diff-code-cell diff-row-empty"><pre class="diff-code">${formatCode("")}</pre></td>
                                <td class="diff-num">${state.newLine++}</td>
                                <td class="diff-code-cell diff-row-added"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                    });
                }
            }

            return rows;
        }

        function buildSideBySideRows(entry) {
            const patch = buildStructuredPatch(entry);
            if (!patch.hunks.length) {
                return `<div class="p-6 text-sm text-slate-500">No hay diferencias detectadas entre los archivos seleccionados.</div>`;
            }

            const state = { oldLine: 1, newLine: 1 };
            let rows = "";
            patch.hunks.forEach((hunk) => {
                rows += `<tr class="diff-separator"><td colspan="4">${escapeHtml(hunk.oldStart + "," + hunk.oldLines + " -> " + hunk.newStart + "," + hunk.newLines)}</td></tr>`;
                rows += renderSideBySideHunk(hunk, state);
            });

            return `
                <div class="diff-split-grid">
                    <div class="diff-pane">
                        <table class="diff-table">
                            <thead>
                                <tr>
                                    <th class="diff-num">MATLAB</th>
                                    <th class="text-left px-3 py-2">${escapeHtml(entry.matlabName)}</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                    <div class="diff-pane">
                        <table class="diff-table">
                            <thead>
                                <tr>
                                    <th class="diff-num">Python</th>
                                    <th class="text-left px-3 py-2">${escapeHtml(entry.pythonName)}</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                </div>
                <table class="diff-table">
                    <colgroup>
                        <col style="width: 56px">
                        <col style="width: calc(50% - 56px)">
                        <col style="width: 56px">
                        <col style="width: calc(50% - 56px)">
                    </colgroup>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        function renderDiff(id) {
            const entry = allEntries.find(item => item.id === id);
            if (!entry) return;

            document.getElementById("selected-status").textContent = entry.statusLabel;
            document.getElementById("selected-status").className = `pill-badge ${kindBadge(entry.kind)}`;
            document.getElementById("selected-category").textContent = entry.category;
            document.getElementById("selected-title").textContent = `${entry.matlabName} → ${entry.pythonName}`;
            document.getElementById("selected-purpose").textContent = entry.purpose;
            document.getElementById("selected-transform").textContent = entry.transform;
            document.getElementById("selected-notes").innerHTML = (entry.notes.length ? entry.notes : ["Sin notas adicionales para este archivo."]).map(note => `<li>${escapeHtml(note)}</li>`).join("");
            document.getElementById("selected-matlab-name").textContent = entry.matlabName;
            document.getElementById("selected-python-name").textContent = entry.pythonName;

            const matlabLink = document.getElementById("selected-matlab-link");
            if (entry.matlabRelPath) {
                matlabLink.textContent = entry.matlabRelPath;
                matlabLink.href = encodeURI(entry.matlabRelPath);
                matlabLink.classList.remove("hidden");
            } else {
                matlabLink.textContent = "Sin archivo MATLAB asociado";
                matlabLink.removeAttribute("href");
            }

            const pythonLink = document.getElementById("selected-python-link");
            if (entry.pythonRelPath) {
                pythonLink.textContent = entry.pythonRelPath;
                pythonLink.href = encodeURI(entry.pythonRelPath);
                pythonLink.classList.remove("hidden");
            } else {
                pythonLink.textContent = "Sin archivo Python asociado";
                pythonLink.removeAttribute("href");
            }

            document.getElementById("selected-stats").innerHTML = [
                statCard("Lineas MATLAB", entry.matlabLines),
                statCard("Lineas Python", entry.pythonLines),
                statCard("Lineas agregadas", entry.addedLines),
                statCard("Lineas removidas", entry.removedLines),
            ].join("");
            const format = document.getElementById("diff-view-mode").value;
            document.getElementById("diff-output").innerHTML =
                format === "side-by-side" ? buildSideBySideRows(entry) : buildUnifiedRows(entry);
        }

        function escapeHtml(value) {
            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;");
        }

        function init() {
            // #region agent log
            fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H2',location:'generate_migration_audit.py:1910',message:'Init iniciado',data:{hasSummaryCards:!!document.getElementById('summary-cards'),hasQuickFacts:!!document.getElementById('quick-facts'),hasTable:!!document.getElementById('transformation-table')},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
            initHeader();
            renderSummary();
            renderTransformationTable();
            buildFilters();
            renderInspectorPicker();
            document.getElementById("search-input").addEventListener("input", (event) => {
                currentSearch = event.target.value;
                renderInspectorPicker();
            });
            document.getElementById("entry-select").addEventListener("change", (event) => {
                currentEntryId = event.target.value;
                renderInspectorPicker();
            });
            document.getElementById("prev-entry").addEventListener("click", () => moveEntry(-1));
            document.getElementById("next-entry").addEventListener("click", () => moveEntry(1));
            document.getElementById("diff-view-mode").addEventListener("change", () => renderDiff(currentEntryId));
            window.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    closeDetailModal();
                }
            });
            lucide.createIcons();
        }

        window.addEventListener("error", (event) => {
            // #region agent log
            fetch('http://127.0.0.1:7567/ingest/2c3908d1-fb5e-4059-90d0-7a5c743c6b70',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e39f56'},body:JSON.stringify({sessionId:'e39f56',runId:'pre-fix',hypothesisId:'H4',location:'generate_migration_audit.py:1941',message:'window error',data:{message:event.message,filename:event.filename,lineno:event.lineno,colno:event.colno},timestamp:Date.now()})}).catch(()=>{});
            // #endregion
        });

        window.onload = init;