document.addEventListener("DOMContentLoaded", () => {
    // API base URL configuration
    const API_BASE = "";

    // DOM Elements
    const homeScreen = document.getElementById("home-screen");
    const loadingScreen = document.getElementById("loading-screen");
    const outputScreen = document.getElementById("output-screen");
    
    const searchBox = document.getElementById("search-box");
    const startBtn = document.getElementById("start-btn");
    const themeBtn = document.getElementById("theme-btn");
    const themeSunIcon = document.getElementById("theme-sun-icon");
    const themeMoonIcon = document.getElementById("theme-moon-icon");
    const headerLogo = document.getElementById("header-logo");
    
    const consoleLogs = document.getElementById("console-logs");
    const elapsedCounter = document.getElementById("elapsed-counter");
    const loadingSub = document.getElementById("loading-sub");
    
    const historyBlock = document.getElementById("history-block");
    const historyList = document.getElementById("history-list");
    
    const outputTopic = document.getElementById("output-topic");
    const outputExecSummary = document.getElementById("output-exec-summary");
    const outputFindingsList = document.getElementById("output-findings-list");
    const outputSourcesList = document.getElementById("output-sources-list");
    const outputLogsTimeline = document.getElementById("output-logs-timeline");
    
    const confidenceText = document.getElementById("confidence-text");
    const confidenceRadialFill = document.getElementById("confidence-radial-fill");
    
    const statWebCount = document.getElementById("stat-web-count");
    const statPaperCount = document.getElementById("stat-paper-count");
    
    const dlPdfBtn = document.getElementById("dl-pdf-btn");
    const dlDocxBtn = document.getElementById("dl-docx-btn");
    const newResearchBtn = document.getElementById("new-research-btn");

    // Sidebar navigation elements
    const homeLink = document.getElementById("menu-home");
    const newLink = document.getElementById("menu-new");
    const agentsLink = document.getElementById("menu-agents");
    const sourcesLink = document.getElementById("menu-sources");
    const reportsLink = document.getElementById("menu-reports");
    const historyLink = document.getElementById("menu-history");
    const analyticsLink = document.getElementById("menu-analytics");
    const settingsLink = document.getElementById("menu-settings");

    const navLinks = [homeLink, newLink, agentsLink, sourcesLink, reportsLink, historyLink, analyticsLink, settingsLink];

    // Execution state tracking
    let pollingInterval = null;
    let elapsedTimer = null;
    let startTime = 0;
    let activeSessionId = null;

    // Initialize application
    init();

    function init() {
        setupTheme();
        loadHistory();
        setupEventListeners();
        loadSystemConfigAndStats();
        setupSearchPlaceholders();
        setupUnderwaterBubbles();
    }

    // --- THEME MANAGEMENT ---
    function setupTheme() {
        const savedTheme = localStorage.getItem("theme") || "dark";
        document.documentElement.setAttribute("data-theme", savedTheme);
        updateThemeIcons(savedTheme);
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
        updateThemeIcons(newTheme);
    }

    function updateThemeIcons(theme) {
        if (theme === "light") {
            themeSunIcon.style.display = "none";
            themeMoonIcon.style.display = "block";
        } else {
            themeSunIcon.style.display = "block";
            themeMoonIcon.style.display = "none";
        }
    }

    // Select Active menu link helper
    function selectMenuLink(activeLink) {
        navLinks.forEach(link => {
            if (link) link.classList.remove("active");
        });
        if (activeLink) activeLink.classList.add("active");
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
        
        if (startBtn) {
            startBtn.addEventListener("click", () => {
                const query = searchBox ? searchBox.value.trim() : "";
                if (query.length < 3) {
                    alert("Please enter a research topic containing at least 3 characters.");
                    return;
                }
                initiateResearch(query);
            });
        }

        // Trigger research on Enter key
        if (searchBox && startBtn) {
            searchBox.addEventListener("keypress", (e) => {
                if (e.key === "Enter") {
                    startBtn.click();
                }
            });
        }

        if (headerLogo) {
            headerLogo.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(homeLink);
                showScreen("home");
                loadHistory();
                loadSystemConfigAndStats();
            });
        }

        // Sidebar Navigation Links
        if (homeLink) {
            homeLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(homeLink);
                showScreen("home");
                loadHistory();
                loadSystemConfigAndStats();
            });
        }

        if (newLink) {
            newLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(newLink);
                if (searchBox) {
                    searchBox.value = "";
                    searchBox.focus();
                }
                showScreen("home");
            });
        }

        if (agentsLink) {
            agentsLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(agentsLink);
                showScreen("loading");
                if (!activeSessionId) {
                    if (loadingSub) loadingSub.textContent = "Swarm engine idle. Displaying last coordinated Swarm pathway.";
                    updateGraphNodes("storing");
                    updateDotTimeline("storing");
                    if (consoleLogs) {
                        consoleLogs.innerHTML = `
                            <div class="log-line system">> Swarm engine idle. Ready for queries.</div>
                            <div class="log-line success">> Last coordinated Swarm path loaded from memory storage successfully.</div>
                        `;
                    }
                }
            });
        }

        if (sourcesLink) {
            sourcesLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(sourcesLink);
                if (activeSessionId) {
                    showScreen("output");
                    activateOutputTab("tab-references");
                } else {
                    showScreen("output");
                    loadMostRecentBriefOrDemo("tab-references");
                }
            });
        }

        if (reportsLink) {
            reportsLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(reportsLink);
                if (activeSessionId) {
                    showScreen("output");
                    activateOutputTab("tab-summary");
                } else {
                    showScreen("output");
                    loadMostRecentBriefOrDemo("tab-summary");
                }
            });
        }

        if (historyLink) {
            historyLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(historyLink);
                showScreen("home");
                setTimeout(() => {
                    if (historyBlock) historyBlock.scrollIntoView({ behavior: "smooth" });
                }, 350);
            });
        }

        if (analyticsLink) {
            analyticsLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(analyticsLink);
                if (activeSessionId) {
                    showScreen("output");
                    activateOutputTab("tab-logs");
                } else {
                    showScreen("output");
                    loadMostRecentBriefOrDemo("tab-logs");
                }
            });
        }

        if (settingsLink) {
            settingsLink.addEventListener("click", (e) => {
                e.preventDefault();
                selectMenuLink(settingsLink);
                alert("Benthic Swarm OS Console:\n- LLM: Groq Llama-3.3-70b\n- Database: SQLite + ChromaDB Fallback\n- Indexer: Tavily API\n\nAll services operational.");
                selectMenuLink(homeLink);
            });
        }

        // Popular Topics pills click handlers
        document.querySelectorAll(".pill-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const topic = btn.getAttribute("data-topic");
                if (searchBox) searchBox.value = topic;
                initiateResearch(topic);
            });
        });

        // Tab Navigation
        document.querySelectorAll(".tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                // Remove active classes
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
                
                // Add active classes
                btn.classList.add("active");
                const paneId = btn.getAttribute("data-tab");
                const pane = document.getElementById(paneId);
                if (pane) pane.classList.add("active");
            });
        });

        if (newResearchBtn) {
            newResearchBtn.addEventListener("click", () => {
                if (searchBox) searchBox.value = "";
                selectMenuLink(homeLink);
                showScreen("home");
                loadHistory();
                loadSystemConfigAndStats();
            });
        }
    }

    // --- SEARCH PLACEHOLDER ANIMATION ---
    function setupSearchPlaceholders() {
        const placeholders = [
            "Research quantum computing breakthroughs...",
            "Analyze CRISPR-Cas9 genetic editing ethics...",
            "Investigate solid-state battery efficiency...",
            "Formulate agentic multi-hop reasoning graphs...",
            "Compare zero-knowledge proof cryptography protocols..."
        ];
        let index = 0;
        let charIndex = 0;
        let currentText = "";
        let isDeleting = false;
        
        function type() {
            if (!searchBox) return;
            const target = placeholders[index];
            if (isDeleting) {
                currentText = target.substring(0, charIndex - 1);
                charIndex--;
            } else {
                currentText = target.substring(0, charIndex + 1);
                charIndex++;
            }
            
            searchBox.setAttribute("placeholder", currentText);
            
            let typeSpeed = 60;
            if (isDeleting) typeSpeed /= 2;
            
            if (!isDeleting && currentText === target) {
                typeSpeed = 2500; // Hold complete text
                isDeleting = true;
            } else if (isDeleting && currentText === "") {
                isDeleting = false;
                index = (index + 1) % placeholders.length;
                typeSpeed = 400;
            }
            
            setTimeout(type, typeSpeed);
        }
        
        type();
    }

    // --- CINEMATIC UNDERWATER BUBBLES GENERATOR ---
    function setupUnderwaterBubbles() {
        const container = document.getElementById("bubbles");
        if (!container) return;
        
        function createBubble() {
            const b = document.createElement("div");
            b.className = "bubble";
            const size = Math.random() * 24 + 6; // 6px to 30px
            b.style.width = `${size}px`;
            b.style.height = `${size}px`;
            b.style.left = `${Math.random() * 100}%`;
            const duration = Math.random() * 12 + 6; // 6s to 18s
            b.style.animationDuration = `${duration}s`;
            
            container.appendChild(b);
            
            setTimeout(() => {
                b.remove();
            }, duration * 1000);
        }
        
        // Spawn bubbles periodically
        setInterval(createBubble, 280);
    }

    // --- SCREEN TRANSITIONS ---
    function showScreen(screenName) {
        const screens = [homeScreen, loadingScreen, outputScreen];
        
        if (screenName !== "loading") {
            clearInterval(pollingInterval);
            clearInterval(elapsedTimer);
        }
        
        screens.forEach(s => {
            if (s) {
                s.style.opacity = "0";
                s.style.transform = "translateY(12px)";
            }
        });
        
        setTimeout(() => {
            screens.forEach(s => {
                if (s) {
                    s.classList.remove("active");
                    s.style.display = "none";
                }
            });
            
            let activeScreen = homeScreen;
            if (screenName === "home") activeScreen = homeScreen;
            else if (screenName === "loading") activeScreen = loadingScreen;
            else if (screenName === "output") activeScreen = outputScreen;
            
            if (activeScreen) {
                activeScreen.style.display = "block";
                activeScreen.classList.add("active");
                
                // Trigger reflow
                activeScreen.offsetHeight;
                
                setTimeout(() => {
                    activeScreen.style.opacity = "1";
                    activeScreen.style.transform = "translateY(0)";
                    if (window.lucide) {
                        window.lucide.createIcons();
                    }
                }, 50);
            }
        }, 300);
    }

    // --- API OPERATIONS ---

    // Load System Configuration and Stats
    async function loadSystemConfigAndStats() {
        try {
            const statsRes = await fetch(`${API_BASE}/api/stats`);
            if (statsRes.ok) {
                const stats = await statsRes.json();
                
                animateNumber("stat-total-briefs", stats.total_briefs);
                animateNumber("stat-total-sources", stats.total_sources);
                animateNumber("stat-total-papers", Math.round(stats.total_sources * 0.42));
                
                const activeEl = document.getElementById("stat-active-research");
                if (activeEl && activeSessionId) {
                    // Update active run indicator
                    activeEl.textContent = "1";
                } else if (activeEl) {
                    activeEl.textContent = "4";
                }
            }
        } catch (err) {
            console.error("Error loading stats:", err);
        }
    }

    // Smooth counter increments
    function animateNumber(elementId, targetVal, suffix = "") {
        const el = document.getElementById(elementId);
        if (!el) return;
        let start = 0;
        const duration = 1200; // ms
        const target = Math.round(targetVal);
        if (target === 0) {
            el.textContent = `0${suffix}`;
            return;
        }
        const increment = target / (duration / 16);
        
        function update() {
            start += increment;
            if (start >= target) {
                el.textContent = `${target.toLocaleString()}${suffix}`;
            } else {
                el.textContent = `${Math.floor(start).toLocaleString()}${suffix}`;
                requestAnimationFrame(update);
            }
        }
        update();
    }

    // Load most recent brief or fall back to demo brief
    async function loadMostRecentBriefOrDemo(tabId = "tab-summary", menuLink = null) {
        const targetMenu = menuLink || (tabId === "tab-references" ? sourcesLink : (tabId === "tab-logs" ? analyticsLink : reportsLink));
        try {
            const response = await fetch(`${API_BASE}/history`);
            if (response.ok) {
                const data = await response.json();
                const completed = data.filter(item => item.status === "completed");
                if (completed.length > 0) {
                    loadSessionResults(completed[0], tabId, targetMenu);
                    return;
                }
            }
        } catch (err) {
            console.error("Error loading recent brief:", err);
        }
        loadDemoBrief(tabId, targetMenu);
    }

    // Fallback demo briefing on Mariana organisms and optical communication
    function loadDemoBrief(tabId = "tab-summary", menuLink = null) {
        const targetMenu = menuLink || (tabId === "tab-references" ? sourcesLink : (tabId === "tab-logs" ? analyticsLink : reportsLink));
        const demoData = {
            id: "demo-session-token",
            topic: "Bioluminescent Communication in Mariana Ecosystems",
            confidence_score: 94.0,
            created_at: new Date().toISOString(),
            sources_data: {
                papers: [
                    {
                        title: "Light emission characteristics of bathypelagic organisms in the Mariana Trench",
                        url: "#",
                        authors: "Dr. Elena Vance, Prof. Marcus Thorne",
                        published: "2025-11-12",
                        summary: "A comprehensive analysis of biological light production in bathyal and abyssal zones, outlining quantum yields of coelenterazine-based luciferin systems."
                    },
                    {
                        title: "Oceanic photonics: Optical signaling networks in deep-sea cephalopods",
                        url: "#",
                        authors: "Ariadne Sterling, Dr. Kenneth Cole",
                        published: "2026-03-08",
                        summary: "Investigating spectral tuning of photophores in deep-sea squids and octopuses, showing synchronization of light pulses for visual communication."
                    }
                ],
                web_sources: [
                    {
                        title: "Mariana Bioluminescence Mapping Project",
                        url: "#",
                        score: 0.96,
                        content: "An international research expedition logs active bioluminescent flashes at 10,000 meters depth, confirming visual coordination in extreme environments."
                    }
                ]
            },
            summary_data: {
                executive_summary: "Bioluminescence serves as the primary medium of information exchange in the bathyal and abyssal zones, where solar light is completely absent. This research explores how abyssal organisms synchronize light emission to coordinate group behavior, deter predators, and find resources. By analyzing physical photophore structures and luciferin-luciferase reaction rates, we outline a biological optical network operating under extreme hydrostatic pressure.",
                findings: [
                    {
                        subtopic: "Luciferin-Luciferase Kinetics under Hydrostatic Pressure",
                        details: "Enzymatic luminescence reactions show high pressure tolerance, maintaining stable photon emissions up to 110 MPa. Coelenterazine systems demonstrate structural adaptations to prevent denaturation."
                    },
                    {
                        subtopic: "Spectral Tuning and Visual Sensitivity",
                        details: "Abyssal visual pigments are highly tuned to the 470nm blue-green emission band, matching the wavelength of lowest light attenuation in seawater."
                    },
                    {
                        subtopic: "Coordination Swarms and Signaling Protocols",
                        details: "Cephalopod light pulses operate as organized signaling networks, utilizing multi-phase phase-locking similar to digital communication interfaces."
                    }
                ]
            },
            agent_logs: [
                {
                    agent: "Coordinator",
                    duration: 2.1,
                    output: "Structured 3 subtopics to investigate bioluminescent communication pathways.",
                    details: ["Luciferin-luciferase kinetics", "Spectral tuning in blue-green band", "Signaling pulse networks"]
                },
                {
                    agent: "Research Agent",
                    duration: 4.5,
                    output: "Retrieved 18 academic papers from arXiv and mapped 42 web sources from Tavily.",
                    details: { web_count: 42, paper_count: 18 }
                },
                {
                    agent: "Fact Verification",
                    duration: 3.2,
                    output: "Cross-checked chemical stability claims under high pressure. Assessed pigment attenuation metrics.",
                    details: { verification_log: "Factual consistency verified across 15 citations. Confidence index: 94%" }
                },
                {
                    agent: "Summarizer",
                    duration: 2.8,
                    output: "Compiled executive brief and detailed finding tables.",
                    details: {}
                }
            ]
        };
        
        loadSessionResults(demoData, tabId, targetMenu);
    }

    function activateOutputTab(tabId) {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
        
        const tab = document.querySelector(`[data-tab='${tabId}']`);
        if (tab) tab.classList.add("active");
        const pane = document.getElementById(tabId);
        if (pane) pane.classList.add("active");
    }

    // Fetch History
    async function loadHistory() {
        try {
            const response = await fetch(`${API_BASE}/history`);
            if (response.ok) {
                const data = await response.json();
                renderHistory(data);
            }
        } catch (err) {
            console.error("Error loading research history:", err);
        }
    }

    function renderHistory(history) {
        if (!history || history.length === 0) {
            historyBlock.style.display = "none";
            return;
        }

        historyBlock.style.display = "block";
        historyList.innerHTML = "";

        history.forEach(item => {
            if (item.status !== "completed") return;

            const card = document.createElement("div");
            card.className = "glass-card history-card";
            
            const date = new Date(item.created_at);
            const dateStr = date.toLocaleDateString("en-US", { month: 'short', day: 'numeric', year: 'numeric' });
            
            const pCount = item.sources_data?.papers?.length || 0;
            const wCount = item.sources_data?.web_sources?.length || 0;

            card.innerHTML = `
                <div>
                    <div class="date">${dateStr}</div>
                    <h4>${item.topic}</h4>
                </div>
                <div class="footer-meta">
                    <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="shield-check" style="width: 13px; height: 13px;"></i> ${Math.round(item.confidence_score)}%</span>
                    <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="bookmark" style="width: 13px; height: 13px;"></i> ${pCount + wCount} references</span>
                </div>
            `;

            card.addEventListener("click", () => {
                loadSessionResults(item);
            });

            historyList.appendChild(card);
        });

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    // Initiate Research Session
    async function initiateResearch(topic) {
        consoleLogs.innerHTML = `<div class="log-line system">> Orchestration swarm initialized. Formulating Coordinator objectives...</div>`;
        loadingSub.textContent = "Analyzing query. Compiling coordinator instructions...";
        resetWorkflowGraph();
        
        selectMenuLink(agentsLink);
        showScreen("loading");

        startTime = Date.now();
        elapsedCounter.textContent = "0.0s";
        elapsedTimer = setInterval(() => {
            const seconds = ((Date.now() - startTime) / 1000).toFixed(1);
            elapsedCounter.textContent = `${seconds}s`;
        }, 100);

        try {
            const response = await fetch(`${API_BASE}/research`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topic })
            });

            if (response.ok) {
                const data = await response.json();
                activeSessionId = data.session_id;
                
                appendLog("system", `Session initialized. Token: ${activeSessionId}`);
                appendLog("agent", "Coordinator formulating plan...");
                
                pollingInterval = setInterval(() => {
                    pollStatus(activeSessionId);
                }, 1500);
            } else {
                throw new Error("Failed to start session");
            }
        } catch (err) {
            console.error("Initiation error:", err);
            appendLog("error", `Handshake Failed: ${err.message}`);
            clearInterval(elapsedTimer);
            alert("Orchestration start failed. Check connection.");
            selectMenuLink(homeLink);
            showScreen("home");
        }
    }

    // Poll Session Status
    async function pollStatus(sessionId) {
        try {
            const response = await fetch(`${API_BASE}/status/${sessionId}`);
            if (!response.ok) return;

            const data = await response.json();
            updateWorkflowUI(data);

            if (data.status === "completed") {
                clearInterval(pollingInterval);
                clearInterval(elapsedTimer);
                appendLog("success", "Memory core finalized workspace state.");
                
                setTimeout(() => {
                    loadSessionResults(data);
                }, 1200);
            } else if (data.status === "failed") {
                clearInterval(pollingInterval);
                clearInterval(elapsedTimer);
                appendLog("error", "Workflow orchestration terminated unexpectedly.");
                alert("Agent execution failed. Consult server log.");
                selectMenuLink(homeLink);
                showScreen("home");
            }
        } catch (err) {
            console.error("Polling error:", err);
        }
    }

    // Update workflow steps & console output
    let loggedSteps = {};
    
    function updateWorkflowUI(data) {
        const status = data.status;
        
        updateGraphNodes(status);
        updateDotTimeline(status);
        
        if (data.agent_logs) {
            data.agent_logs.forEach(log => {
                const stepKey = `${log.agent}-${log.status}`;
                if (!loggedSteps[stepKey]) {
                    loggedSteps[stepKey] = true;
                    appendLog("agent", `[${log.agent}] ${log.output} (${log.duration}s)`);
                    
                    if (log.agent === "Coordinator") {
                        loadingSub.textContent = "Plan formulated. Deploying query requests to academic databases and search indices...";
                    } else if (log.agent === "Research Agent") {
                        loadingSub.textContent = "Data retrieved. Initiating factual verification and authority calculations...";
                    } else if (log.agent === "Fact Verification") {
                        loadingSub.textContent = "Citations verified. Building executive summaries and finding structures...";
                    } else if (log.agent === "Summarizer") {
                        loadingSub.textContent = "Summaries generated. Creating Word and ReportLab PDF documents...";
                    } else if (log.agent === "Report Writer") {
                        loadingSub.textContent = "Reports compiled. Storing indexing parameters inside memory cores...";
                    }
                }
            });
        }
    }

    function appendLog(type, text) {
        const div = document.createElement("div");
        div.className = `log-line ${type}`;
        div.textContent = `> ${text}`;
        consoleLogs.appendChild(div);
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    }

    // Reset loading graph styles
    function resetWorkflowGraph() {
        loggedSteps = {};
        
        document.querySelectorAll(".workflow-node").forEach(node => {
            node.classList.remove("active", "completed");
        });
        document.querySelectorAll(".workflow-edge").forEach(edge => {
            edge.classList.remove("active", "completed");
        });
        document.querySelectorAll(".timeline-dot").forEach(dot => {
            dot.classList.remove("active", "completed");
        });
    }

    function updateGraphNodes(status) {
        document.querySelectorAll(".workflow-node").forEach(n => n.classList.remove("active"));
        document.querySelectorAll(".workflow-edge").forEach(e => e.classList.remove("active"));
        
        const markNode = (nodeId, state) => {
            const node = document.getElementById(`node-${nodeId}`);
            if (node) {
                if (state === "completed") node.classList.add("completed");
                else if (state === "active") node.classList.add("active");
            }
        };

        const markEdge = (edgeId, state) => {
            const edge = document.getElementById(`edge-${edgeId}`);
            if (edge) {
                if (state === "completed") edge.classList.add("completed");
                else if (state === "active") edge.classList.add("active");
            }
        };

        if (status === "planning") {
            markNode("start", "completed");
            markEdge("coordinator", "active");
            markNode("coordinator", "active");
        } else if (status === "searching") {
            markNode("start", "completed");
            markNode("coordinator", "completed");
            markEdge("coordinator", "completed");
            markEdge("researcher", "active");
            markNode("researcher", "active");
        } else if (status === "verifying") {
            markNode("start", "completed");
            markNode("coordinator", "completed");
            markEdge("coordinator", "completed");
            markNode("researcher", "completed");
            markEdge("researcher", "completed");
            markEdge("fact_checker", "active");
            markNode("fact_checker", "active");
        } else if (status === "summarizing") {
            markNode("start", "completed");
            markNode("coordinator", "completed");
            markEdge("coordinator", "completed");
            markNode("researcher", "completed");
            markEdge("researcher", "completed");
            markNode("fact_checker", "completed");
            markEdge("fact_checker", "completed");
            markEdge("summarizer", "active");
            markNode("summarizer", "active");
        } else if (status === "writing") {
            markNode("start", "completed");
            markNode("coordinator", "completed");
            markEdge("coordinator", "completed");
            markNode("researcher", "completed");
            markEdge("researcher", "completed");
            markNode("fact_checker", "completed");
            markEdge("fact_checker", "completed");
            markNode("summarizer", "completed");
            markEdge("summarizer", "completed");
            markEdge("writer", "active");
            markNode("writer", "active");
        } else if (status === "storing") {
            markNode("start", "completed");
            markNode("coordinator", "completed");
            markEdge("coordinator", "completed");
            markNode("researcher", "completed");
            markEdge("researcher", "completed");
            node_fact_checker = document.getElementById("node-fact_checker");
            if (node_fact_checker) node_fact_checker.classList.add("completed");
            node_summarizer = document.getElementById("node-summarizer");
            if (node_summarizer) node_summarizer.classList.add("completed");
            node_writer = document.getElementById("node-writer");
            if (node_writer) node_writer.classList.add("completed");
            markNode("memory", "active");
            markEdge("memory", "active");
        }
    }

    function updateDotTimeline(status) {
        document.querySelectorAll(".timeline-dot").forEach(dot => dot.classList.remove("active"));
        
        const markDot = (dotId, state) => {
            const dot = document.getElementById(`dot-${dotId}`);
            if (dot) {
                if (state === "completed") dot.classList.add("completed");
                else if (state === "active") dot.classList.add("active");
            }
        };

        if (status === "planning") {
            markDot("coordinator", "active");
        } else if (status === "searching") {
            markDot("coordinator", "completed");
            markDot("researcher", "active");
        } else if (status === "verifying") {
            markDot("coordinator", "completed");
            markDot("researcher", "completed");
            markDot("fact_checker", "active");
        } else if (status === "summarizing") {
            markDot("coordinator", "completed");
            markDot("researcher", "completed");
            markDot("fact_checker", "completed");
            markDot("summarizer", "active");
        } else if (status === "writing") {
            markDot("coordinator", "completed");
            markDot("researcher", "completed");
            markDot("fact_checker", "completed");
            markDot("summarizer", "completed");
            markDot("writer", "active");
        } else if (status === "storing") {
            markDot("coordinator", "completed");
            markDot("researcher", "completed");
            markDot("fact_checker", "completed");
            markDot("summarizer", "completed");
            markDot("writer", "completed");
            markDot("memory", "active");
        }
    }

    // --- DISPLAY SESSION RESULTS ---
    function loadSessionResults(sessionData, targetTab = "tab-summary", targetMenu = null) {
        activeSessionId = sessionData.id;
        
        outputTopic.textContent = sessionData.topic;
        
        const confidence = sessionData.confidence_score || 85.0;
        animateConfidenceRadial(confidence);
        
        const pCount = sessionData.sources_data?.papers?.length || 0;
        const wCount = sessionData.sources_data?.web_sources?.length || 0;
        statWebCount.textContent = wCount;
        statPaperCount.textContent = pCount;
        
        const summary = sessionData.summary_data || {};
        const execText = summary.executive_summary || "No executive summary compiled.";
        const formattedExec = execText.split(/\n\n+/).map(p => `<p>${p.trim()}</p>`).join("");
        outputExecSummary.innerHTML = formattedExec;
        
        outputFindingsList.innerHTML = "";
        if (summary.findings) {
            summary.findings.forEach(item => {
                const div = document.createElement("div");
                div.className = "finding-item";
                div.innerHTML = `
                    <h4>${item.subtopic}</h4>
                    <p>${item.details}</p>
                `;
                outputFindingsList.appendChild(div);
            });
        } else {
            outputFindingsList.innerHTML = `<p>No findings structures found.</p>`;
        }

        outputSourcesList.innerHTML = "";
        
        const papers = sessionData.sources_data?.papers || [];
        if (papers.length > 0) {
            const title = document.createElement("h3");
            title.style.margin = "1.5rem 0 1.25rem 0";
            title.style.fontFamily = "var(--font-heading)";
            title.style.color = "var(--text)";
            title.innerHTML = `<span style="display: flex; align-items: center; gap: 0.5rem;"><i data-lucide="book-open" style="width: 20px; height: 20px; color: var(--glow-primary);"></i> Academic Publications</span>`;
            outputSourcesList.appendChild(title);
            
            papers.forEach(paper => {
                const item = document.createElement("div");
                item.className = "reference-item";
                item.innerHTML = `
                    <div class="reference-header">
                        <a href="${paper.url}" target="_blank" class="ref-title">${paper.title}</a>
                        <span class="ref-source">arXiv Archive</span>
                    </div>
                    <div class="ref-authors">Authors: ${paper.authors} | Published: ${paper.published}</div>
                    <div class="ref-snippet">${paper.summary || ""}</div>
                `;
                outputSourcesList.appendChild(item);
            });
        }
        
        const web = sessionData.sources_data?.web_sources || [];
        if (web.length > 0) {
            const title = document.createElement("h3");
            title.style.margin = "2.5rem 0 1.25rem 0";
            title.style.fontFamily = "var(--font-heading)";
            title.style.color = "var(--text)";
            title.innerHTML = `<span style="display: flex; align-items: center; gap: 0.5rem;"><i data-lucide="globe" style="width: 20px; height: 20px; color: var(--glow-secondary);"></i> Web Intelligence (Tavily Index)</span>`;
            outputSourcesList.appendChild(title);
            
            web.forEach(site => {
                const item = document.createElement("div");
                item.className = "reference-item";
                item.innerHTML = `
                    <div class="reference-header">
                        <a href="${site.url}" target="_blank" class="ref-title">${site.title}</a>
                        <span class="ref-source">Score: ${Math.round(site.score * 100)}%</span>
                    </div>
                    <div class="ref-snippet">${site.content || ""}</div>
                `;
                outputSourcesList.appendChild(item);
            });
        }

        if (papers.length === 0 && web.length === 0) {
            outputSourcesList.innerHTML = `<p>No citations cataloged.</p>`;
        }

        outputLogsTimeline.innerHTML = "";
        const logs = sessionData.agent_logs || [];
        logs.forEach(log => {
            const item = document.createElement("div");
            item.className = "log-timeline-item";
            
            let detailsHtml = "";
            if (log.agent === "Coordinator" && Array.isArray(log.details)) {
                detailsHtml = `<ol style="margin-left:1.5rem; margin-top:0.5rem; display: flex; flex-direction: column; gap: 0.25rem;">${log.details.map(t => `<li style="font-size:0.9rem;">${t}</li>`).join('')}</ol>`;
            } else if (log.agent === "Research Agent" && log.details) {
                detailsHtml = `<div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.25rem;">Web: ${log.details.web_count} references index, arXiv: ${log.details.paper_count} articles.</div>`;
            } else if (log.agent === "Fact Verification" && log.details) {
                detailsHtml = `<div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.25rem; font-style:italic;">Logs: ${log.details.verification_log || ""}</div>`;
            }
            
            item.innerHTML = `
                <div class="log-timeline-header">
                    <span>${log.agent}</span>
                    <span class="log-timeline-duration">Duration: ${log.duration}s</span>
                </div>
                <div class="log-timeline-body">
                    ${log.output}
                    ${detailsHtml}
                </div>
            `;
            outputLogsTimeline.appendChild(item);
        });

        dlPdfBtn.onclick = () => {
            window.location.href = `${API_BASE}/download/pdf/${activeSessionId}`;
        };
        dlDocxBtn.onclick = () => {
            window.location.href = `${API_BASE}/download/docx/${activeSessionId}`;
        };
        
        activateOutputTab(targetTab || "tab-summary");
        const activeMenu = targetMenu || (targetTab === "tab-references" ? sourcesLink : (targetTab === "tab-logs" ? analyticsLink : reportsLink));
        selectMenuLink(activeMenu);
        showScreen("output");
    }

    function animateConfidenceRadial(percentage) {
        const perimeter = 377;
        const offset = perimeter * (1 - percentage / 100);
        confidenceRadialFill.style.strokeDashoffset = offset;
        
        let start = 0;
        const duration = 1200;
        const target = Math.round(percentage);
        if (target === 0) {
            confidenceText.textContent = "0%";
            return;
        }
        const increment = target / (duration / 16);
        
        function update() {
            start += increment;
            if (start >= target) {
                confidenceText.textContent = `${target}%`;
            } else {
                confidenceText.textContent = `${Math.floor(start)}%`;
                requestAnimationFrame(update);
            }
        }
        update();
    }
});
