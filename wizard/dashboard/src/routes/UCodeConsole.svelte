<script>
  import { onMount, onDestroy } from "svelte";
  import { getAdminToken, buildAuthHeaders } from "$lib/services/auth";
  import { apiFetch } from "$lib/services/apiBase";
  import {
    fetchUCodeCommands,
    fetchUCodeHotkeys,
    fetchOkStatus,
    fetchOkHistory,
    setOkDefaultModel,
    dispatchUCodeCommand,
    fetchUCodeUser,
    fetchUCodeUsers,
    switchUCodeUser,
    setUCodeUserRole,
    fetchProviderDashboard,
    fetchDevStatus,
    toggleDevMode,
    restartDevMode,
    fetchMonitoringDiagnostics,
    fetchWizardHealth,
  } from "$lib/services/ucodeService";
  import { ansiToHtml } from "$lib/utils/ansi";
  import { createEmptyTile } from "$lib/types/layer";
  import TileGrid from "$lib/components/TileGrid.svelte";
  import StoryRenderer from "$lib/components/StoryRenderer.svelte";
  import TerminalButton from "$lib/components/terminal/TerminalButton.svelte";
  import TerminalChip from "$lib/components/terminal/TerminalChip.svelte";

  let adminToken = "";
  let hasAdminToken = false;
  let commandInput = "";
  let history = [];
  let commands = [];
  let suggestions = [];
  let helperLine1 = "";
  let helperLine2 = "";
  let selectedCommand = null;
  let okStatus = null;
  let okHistory = [];
  let okModel = "";
  let okModels = [];
  let okProfile = "core";
  let okSaveStatus = "";
  let okFilePath = "";
  let okRange = "";
  let logStreamActive = false;
  let logStreamError = "";
  let logEntries = [];
  let logComponent = "wizard";
  let logName = "wizard-server";
  let logLimit = 200;
  let logAbort = null;
  let hotkeys = [];
  let currentUser = null;
  let userList = [];
  let ghostMode = false;
  let devStatus = null;
  let devRequirements = null;
  let devGateError = "";
  let canDevMode = false;
  let wizardUp = false;
  let devWorkspaceUp = false;
  let memPercent = "?";
  let cpuPercent = "?";
  let quotas = {};
  let statusTimer;
  let userTimer;
  let loading = false;
  let error = "";

  const historyKey = "wizardUcodeHistory";
  const lastUserKey = "wizardUcodeLastUser";
  const okModelKey = "wizardOkModel";

  const okSubcommands = [
    {
      name: "EXPLAIN",
      help_text: "Explain a code file",
      syntax: "OK EXPLAIN <file> [start end] [--cloud]",
    },
    {
      name: "DIFF",
      help_text: "Propose a diff for a file",
      syntax: "OK DIFF <file> [start end] [--cloud]",
    },
    {
      name: "PATCH",
      help_text: "Draft a patch for a file",
      syntax: "OK PATCH <file> [start end] [--cloud]",
    },
    {
      name: "LOCAL",
      help_text: "Show recent OK local outputs",
      syntax: "OK LOCAL [N]",
    },
  ];

  const hotkeyCommandMap = {
    F1: "STATUS",
    F2: "LOGS",
    F3: "REPAIR",
    F4: "REBOOT",
    F5: "WIZARD",
    F6: "PATTERN",
    F7: "SONIC",
    F8: "HELP",
  };

  function loadHistory() {
    if (typeof localStorage === "undefined") return;
    try {
      const raw = localStorage.getItem(historyKey);
      if (raw) {
        history = JSON.parse(raw);
      }
    } catch {
      history = [];
    }
  }

  function persistHistory() {
    if (typeof localStorage === "undefined") return;
    localStorage.setItem(historyKey, JSON.stringify(history.slice(-100)));
  }

  function pushHistory(entry) {
    history = [...history, entry].slice(-100);
    persistHistory();
  }

  function updateHistory(id, patch) {
    history = history.map((item) => (item.id === id ? { ...item, ...patch } : item));
    persistHistory();
  }

  function normalizeInput(value) {
    return (value || "").trim();
  }

  function extractPrefix(input) {
    const trimmed = normalizeInput(input);
    if (!trimmed) return "";
    if (trimmed.startsWith("/")) return "";
    if (trimmed.startsWith(":")) return trimmed.slice(1);
    return trimmed;
  }

  function computeSuggestions() {
    const trimmed = normalizeInput(commandInput);
    if (!trimmed) {
      suggestions = commands.slice(0, 6);
      return;
    }
    if (trimmed.startsWith("/")) {
      suggestions = [];
      return;
    }

    const okMatch = trimmed.toUpperCase();
    if (okMatch.startsWith("OK")) {
      const parts = trimmed.split(/\s+/).filter(Boolean);
      if (parts.length <= 1) {
        suggestions = okSubcommands.map((item) => ({
          name: `OK ${item.name}`,
          help_text: item.help_text,
          syntax: item.syntax,
          category: "AI",
        }));
        return;
      }
      const subPrefix = parts[1].toUpperCase();
      suggestions = okSubcommands
        .filter((item) => item.name.startsWith(subPrefix) || item.name.includes(subPrefix))
        .map((item) => ({
          name: `OK ${item.name}`,
          help_text: item.help_text,
          syntax: item.syntax,
          category: "AI",
        }));
      return;
    }

    const prefix = extractPrefix(trimmed).split(/\s+/)[0].toUpperCase();
    if (!prefix) {
      suggestions = commands.slice(0, 6);
      return;
    }

    const matches = commands.filter((cmd) =>
      cmd.name.startsWith(prefix) || cmd.name.includes(prefix),
    );
    suggestions = matches.slice(0, 6);
  }

  function updateHelperLines() {
    if (!suggestions.length) {
      helperLine1 = "-> No matching commands";
      helperLine2 = "-> Tip: '?' or 'OK' for AI, '/' for commands";
      return;
    }
    const names = suggestions.slice(0, 3).map((s) => s.name).join(", ");
    const extra = suggestions.length > 3 ? ` (+${suggestions.length - 3} more)` : "";
    helperLine1 = `-> Suggestions: ${names}${extra}`;
    const first = suggestions[0];
    const help = first.help_text || "";
    const syntax = first.syntax ? ` | ${first.syntax}` : "";
    helperLine2 = `-> ${help}${syntax}`;
  }

  $: computeSuggestions();
  $: updateHelperLines();
  $: selectedCommand = suggestions[0] || null;

  function buildGridLayer(result) {
    const grid = result?.grid;
    if (!grid) return null;
    const rows = grid.split("\n");
    const height = result.height || rows.length;
    const width = result.width || Math.max(...rows.map((row) => row.length));

    const tiles = Array.from({ length: height }, (_, rowIndex) => {
      const row = rows[rowIndex] || "";
      return Array.from({ length: width }, (_, colIndex) => {
        const char = row[colIndex] || " ";
        return {
          ...createEmptyTile(),
          char,
          code: char.codePointAt(0) || 32,
        };
      });
    });

    return {
      id: "preview",
      name: "Map Preview",
      width,
      height,
      tiles,
      visible: true,
      opacity: 1,
      locked: true,
      zIndex: 0,
      blendMode: "normal",
    };
  }

  function buildStoryState(result) {
    if (result?.story_form) {
      const form = result.story_form;
      return {
        frontmatter: {
          title: form.title || "Story",
          description: form.text || "",
        },
        sections: (form.sections || []).map((section) => ({
          title: section.title || section.name || "",
          content: section.text || section.description || "",
          questions: section.fields || section.questions || [],
        })),
        answers: {},
        currentSectionIndex: 0,
        isComplete: false,
      };
    }
    if (result?.sections && result?.frontmatter) {
      return {
        frontmatter: {
          title: result.frontmatter.title || "Story",
          description: result.frontmatter.description || "",
        },
        sections: (result.sections || []).map((section) => ({
          title: section.title || section.name || "",
          content: section.text || section.description || "",
          questions: section.questions || section.fields || [],
        })),
        answers: {},
        currentSectionIndex: 0,
        isComplete: false,
      };
    }
    return null;
  }

  function renderOutput(entry) {
    const text = entry.displayOutput ?? entry.output ?? "";
    return ansiToHtml(text);
  }

  function startStreaming(entryId, text) {
    const lines = (text || "").split("\n");
    if (!lines.length) return;
    let idx = 0;
    const interval = setInterval(() => {
      idx += 1;
      const chunk = lines.slice(0, idx).join("\n");
      updateHistory(entryId, { displayOutput: chunk, streaming: idx < lines.length });
      if (idx >= lines.length) {
        clearInterval(interval);
      }
    }, 30);
  }

  async function handleDispatch(commandOverride) {
    const command = normalizeInput(commandOverride || commandInput);
    if (!command) return;
    if (!adminToken) {
      error = "Admin token required to dispatch commands.";
      return;
    }

    const entry = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      command,
      createdAt: new Date().toISOString(),
      status: "pending",
      output: "",
      displayOutput: "",
      rendered: "",
      ok: null,
      okHistory: null,
      gridLayer: null,
      storyState: null,
      storySubmitStatus: "",
      streaming: false,
    };

    pushHistory(entry);
    commandInput = "";

    try {
      const payload = {
        command,
        ok_model: okModel || undefined,
      };
      const streamRes = await fetch("/api/ucode/dispatch/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...buildAuthHeaders(adminToken) },
        body: JSON.stringify(payload),
      });

      if (!streamRes.ok || !streamRes.body) {
        const response = await dispatchUCodeCommand(adminToken, payload);
        const result = response.result || {};
        const output =
          result.output ||
          result.help ||
          result.text ||
          result.message ||
          response.rendered ||
          "";

        const gridLayer = buildGridLayer(result);
        const storyState = buildStoryState(result);
        const okEntry = response.ok || null;
        const okHistoryResponse = response.ok_history || null;

        updateHistory(entry.id, {
          status: result.status || "success",
          output,
          rendered: response.rendered || "",
          ok: okEntry,
          okHistory: okHistoryResponse,
          gridLayer,
          storyState,
        });

        if (output) {
          startStreaming(entry.id, output);
        }

        if (okEntry) {
          okHistory = [okEntry, ...okHistory].slice(0, 10);
        }
        if (okHistoryResponse) {
          okHistory = okHistoryResponse.slice().reverse();
        }
        return;
      }

      const reader = streamRes.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let streamed = "";

      const handleEvent = (eventName, data) => {
        if (eventName === "chunk") {
          const text = data?.text ?? "";
          streamed += text;
          updateHistory(entry.id, {
            displayOutput: streamed,
            output: streamed,
            status: "streaming",
          });
          return;
        }
        if (eventName === "result") {
          const response = data || {};
          const result = response.result || {};
          const output =
            streamed ||
            result.output ||
            result.help ||
            result.text ||
            result.message ||
            response.rendered ||
            "";
          const gridLayer = buildGridLayer(result);
          const storyState = buildStoryState(result);
          const okEntry = response.ok || null;
          const okHistoryResponse = response.ok_history || null;

          updateHistory(entry.id, {
            status: result.status || "success",
            output,
            displayOutput: output,
            rendered: response.rendered || "",
            ok: okEntry,
            okHistory: okHistoryResponse,
            gridLayer,
            storyState,
          });

          if (okEntry) {
            okHistory = [okEntry, ...okHistory].slice(0, 10);
          }
          if (okHistoryResponse) {
            okHistory = okHistoryResponse.slice().reverse();
          }
          return;
        }
        if (eventName === "error") {
          updateHistory(entry.id, {
            status: "error",
            output: data?.error || "Stream error",
          });
        }
      };

      const parseSse = (chunk) => {
        buffer += chunk;
        let idx = buffer.indexOf("\n\n");
        while (idx !== -1) {
          const raw = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          const lines = raw.split("\n");
          let eventName = "message";
          const dataLines = [];
          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventName = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              dataLines.push(line.slice(5).trimStart());
            }
          }
          const dataStr = dataLines.join("\n");
          let payload = dataStr;
          try {
            payload = JSON.parse(dataStr);
          } catch {
            payload = { text: dataStr };
          }
          handleEvent(eventName, payload);
          idx = buffer.indexOf("\n\n");
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        parseSse(decoder.decode(value, { stream: true }));
      }
    } catch (err) {
      updateHistory(entry.id, {
        status: "error",
        output: err.message || String(err),
      });
    }
  }

  async function submitStory(entryId, storyState, answers) {
    if (!storyState?.frontmatter?.submit_endpoint) return;
    try {
      const res = await apiFetch(storyState.frontmatter.submit_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...buildAuthHeaders(adminToken) },
        body: JSON.stringify({ answers }),
      });
      if (!res.ok) {
        const detail = await res.text();
        updateHistory(entryId, {
          storySubmitStatus: detail || `HTTP ${res.status}`,
        });
        pushHistory({
          id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
          command: "SETUP SUBMIT",
          createdAt: new Date().toISOString(),
          status: "error",
          output: detail || `HTTP ${res.status}`,
          displayOutput: detail || `HTTP ${res.status}`,
        });
        return;
      }
      updateHistory(entryId, {
        storySubmitStatus: "Story submitted successfully.",
      });
      pushHistory({
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        command: "SETUP SUBMIT",
        createdAt: new Date().toISOString(),
        status: "success",
        output: "Story submitted successfully.",
        displayOutput: "Story submitted successfully.",
      });
      await apiFetch("/api/logs/toast", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...buildAuthHeaders(adminToken) },
        body: JSON.stringify({
          severity: "success",
          title: "Setup submission",
          message: "Wizard setup story submitted from uCODE console.",
          meta: {
            command: "SETUP",
            source: "ucode-console",
          },
        }),
      });
    } catch (err) {
      updateHistory(entryId, {
        storySubmitStatus: err.message || String(err),
      });
      pushHistory({
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        command: "SETUP SUBMIT",
        createdAt: new Date().toISOString(),
        status: "error",
        output: err.message || String(err),
        displayOutput: err.message || String(err),
      });
      await apiFetch("/api/logs/toast", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...buildAuthHeaders(adminToken) },
        body: JSON.stringify({
          severity: "error",
          title: "Setup submission failed",
          message: err.message || String(err),
          meta: {
            command: "SETUP",
            source: "ucode-console",
          },
        }),
      });
    }
  }

  function handleSetupClick() {
    handleDispatch("SETUP");
  }

  function handleHotkeyClick(key) {
    const command = hotkeyCommandMap[key];
    if (command) {
      handleDispatch(command);
    }
  }

  function setQuickOkCommand(mode) {
    if (!okFilePath) return;
    const range = okRange ? ` ${okRange}` : "";
    handleDispatch(`OK ${mode} ${okFilePath}${range}`);
  }

  async function refreshStatus() {
    try {
      wizardUp = await fetchWizardHealth();
    } catch {
      wizardUp = false;
    }

    if (!adminToken) {
      devWorkspaceUp = false;
      memPercent = "?";
      cpuPercent = "?";
      return;
    }

    try {
      devStatus = await fetchDevStatus(adminToken);
      devWorkspaceUp = !!devStatus?.active;
      devRequirements = devStatus?.requirements || null;
      devGateError = "";
    } catch {
      devWorkspaceUp = false;
      devGateError = "Dev mode unavailable (admin + /dev required).";
    }

    try {
      const diag = await fetchMonitoringDiagnostics(adminToken);
      const stats = diag?.system?.stats || {};
      memPercent = stats?.memory?.percent ?? "?";
      cpuPercent = stats?.cpu?.percent ?? "?";
    } catch {
      memPercent = "?";
      cpuPercent = "?";
    }

    try {
      const providerDash = await fetchProviderDashboard(adminToken);
      quotas = providerDash?.quotas || {};
    } catch {
      quotas = {};
    }
  }

  async function refreshOkStatus() {
    if (!adminToken) return;
    try {
      const payload = await fetchOkStatus(adminToken);
      okStatus = payload.ok || null;
      const models = okStatus?.models || [];
      const declared = okStatus?.declared_models || [];
      okModels = Array.from(new Set([...(models || []), ...(declared || [])])).filter(Boolean);
      if (!okModel) {
        okModel =
          (typeof localStorage !== "undefined" && localStorage.getItem(okModelKey)) ||
          okStatus?.default_model ||
          okModels[0] ||
          "";
      }
    } catch (err) {
      okStatus = null;
    }
  }

  async function refreshOkHistory() {
    if (!adminToken) return;
    try {
      const payload = await fetchOkHistory(adminToken);
      okHistory = (payload.history || []).slice().reverse();
    } catch {
      okHistory = [];
    }
  }

  async function refreshUsers() {
    if (!adminToken) return;
    try {
      const payload = await fetchUCodeUser(adminToken);
      currentUser = payload.user || null;
      ghostMode = !!payload.ghost_mode;
      if (currentUser && !ghostMode) {
        localStorage.setItem(lastUserKey, currentUser.username);
      }
    } catch {
      currentUser = null;
      ghostMode = false;
    }

    try {
      const payload = await fetchUCodeUsers(adminToken);
      userList = payload.users || [];
    } catch {
      userList = [];
    }
  }

  async function handleGhostToggle() {
    if (!adminToken) return;
    if (ghostMode) {
      const fallback = localStorage.getItem(lastUserKey) || "admin";
      await switchUCodeUser(adminToken, fallback);
    } else {
      await switchUCodeUser(adminToken, "ghost");
    }
    await refreshUsers();
  }

  async function handleUserSwitch(event) {
    const username = event.target.value;
    if (!username) return;
    await switchUCodeUser(adminToken, username);
    await refreshUsers();
  }

  async function handleRoleChange(event) {
    const role = event.target.value;
    if (!role || !currentUser) return;
    await setUCodeUserRole(adminToken, currentUser.username, role);
    await refreshUsers();
  }

  async function handleDevToggle(active) {
    if (!adminToken || !canDevMode) return;
    try {
      await toggleDevMode(adminToken, active);
      devGateError = "";
      await refreshStatus();
    } catch (err) {
      devGateError = err.message || String(err);
    }
  }

  async function handleDevRestart() {
    if (!adminToken || !canDevMode) return;
    try {
      await restartDevMode(adminToken);
      devGateError = "";
      await refreshStatus();
    } catch (err) {
      devGateError = err.message || String(err);
    }
  }

  function stopLogStream() {
    if (logAbort) {
      logAbort.abort();
      logAbort = null;
    }
    logStreamActive = false;
  }

  async function startLogStream() {
    if (!adminToken) return;
    stopLogStream();
    logStreamError = "";
    logEntries = [];
    logStreamActive = true;
    logAbort = new AbortController();
    try {
      const qs = new URLSearchParams({
        component: logComponent,
        name: logName,
        limit: String(logLimit || 200),
      });
      const res = await fetch(`/api/logs/stream?${qs.toString()}`, {
        headers: buildAuthHeaders(adminToken),
        signal: logAbort.signal,
      });
      if (!res.ok || !res.body) {
        const detail = await res.text();
        throw new Error(detail || `HTTP ${res.status}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      const handleEvent = (block) => {
        const lines = block.split("\n");
        let eventType = "message";
        let data = "";
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            data += line.slice(5).trim();
          }
        }
        if (eventType === "log" && data) {
          logEntries = [...logEntries, data].slice(-200);
        } else if (eventType === "error" && data) {
          logStreamError = data;
        }
      };
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let idx = buffer.indexOf("\n\n");
        while (idx !== -1) {
          const chunk = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          if (chunk.trim()) {
            handleEvent(chunk);
          }
          idx = buffer.indexOf("\n\n");
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        logStreamError = err.message || String(err);
      }
    } finally {
      logStreamActive = false;
    }
  }

  function handleInputKeydown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleDispatch();
    }
  }

  function handleGlobalKeydown(event) {
    if (/^F\d$/.test(event.key)) {
      handleHotkeyClick(event.key);
    }
  }

  function handleModelChange(event) {
    okModel = event.target.value;
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(okModelKey, okModel);
    }
  }

  async function handleOkSave() {
    if (!adminToken || !okModel) return;
    if (okProfile === "dev" && !okStatus?.dev_mode_active) {
      okSaveStatus = "Coding assistant profile requires active Dev Mode.";
      return;
    }
    okSaveStatus = "";
    try {
      await setOkDefaultModel(adminToken, okModel, okProfile);
      okSaveStatus = `Saved ${okProfile} default to ${okModel}.`;
      await refreshOkStatus();
    } catch (err) {
      okSaveStatus = err.message || String(err);
    }
  }

  async function bootstrap() {
    loading = true;
    error = "";
    try {
      adminToken = getAdminToken();
      hasAdminToken = !!adminToken;
      loadHistory();

      if (!adminToken) {
        loading = false;
        return;
      }

      const [commandPayload, hotkeyPayload] = await Promise.all([
        fetchUCodeCommands(adminToken),
        fetchUCodeHotkeys(adminToken),
      ]);
      commands = commandPayload.commands || [];
      hotkeys = hotkeyPayload.hotkeys || [];

      await refreshOkStatus();
      await refreshOkHistory();
      await refreshUsers();
      await refreshStatus();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  $: canDevMode =
    (currentUser?.role || "").toLowerCase() === "admin" &&
    !!devRequirements?.dev_root_present &&
    !!devRequirements?.dev_template_present;

  onMount(() => {
    bootstrap();
    window.addEventListener("keydown", handleGlobalKeydown);
    statusTimer = setInterval(refreshStatus, 8000);
    userTimer = setInterval(refreshUsers, 15000);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleGlobalKeydown);
    if (statusTimer) clearInterval(statusTimer);
    if (userTimer) clearInterval(userTimer);
    stopLogStream();
  });
</script>

<div class="ucode-shell">
  <div class="ucode-main">
    <header class="ucode-header">
      <div>
        <h1 class="text-3xl font-bold text-white">Terminal</h1>
        <p class="text-gray-400">
          Live command console for Wizard services + Vibe CLI. Prefix with ':' for core commands, 'OK' for local Vibe, '/' for shell.
        </p>
      </div>
      <div class="status-strip">
        <TerminalChip>WIZ {wizardUp ? "UP" : "DOWN"}</TerminalChip>
        <TerminalChip>DEVWK {devWorkspaceUp ? "UP" : "DOWN"}</TerminalChip>
        <TerminalChip>CPU {cpuPercent}%</TerminalChip>
        <TerminalChip>MEM {memPercent}%</TerminalChip>
        {#if devStatus}
          <TerminalChip>DEV {devStatus.active ? "ON" : "OFF"}</TerminalChip>
        {/if}
      </div>
      {#if okStatus?.default_models}
        <div class="defaults-banner">
          <span class="defaults-label">OK defaults</span>
          <span class="defaults-value">
            core {okStatus.default_models.core || "—"} · dev {okStatus.default_models.dev || "—"}
          </span>
        </div>
      {/if}
    </header>

    {#if !hasAdminToken}
      <div class="bg-amber-900/40 border border-amber-700 text-amber-100 rounded-lg p-4 text-sm">
        Admin token missing. Set it in the Config page to enable console commands.
      </div>
    {/if}

    {#if error}
      <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
        {error}
      </div>
    {/if}

    <div class="ucode-console wiz-terminal-panel">
      <div class="ucode-history">
        {#if loading}
          <div class="text-gray-400">Loading console...</div>
        {:else if history.length === 0}
          <div class="text-gray-400">No commands yet. Try `STATUS`, `MAP`, or `OK EXPLAIN core/tui/ucode.py`.</div>
        {:else}
          {#each history as entry (entry.id)}
            <div class="history-entry">
              <div class="entry-header">
                <div class="entry-command">{entry.command}</div>
                <div class="entry-meta">
                  <span class={`status-pill status-${entry.status}`}>{entry.status}</span>
                  <span class="entry-time">{new Date(entry.createdAt).toLocaleTimeString()}</span>
                </div>
              </div>
              {#if entry.ok}
                <div class="ok-block">
                  <div class="ok-title">OK {entry.ok.mode} | {entry.ok.model} | {entry.ok.source}</div>
                  {#if entry.ok.file_path}
                    <div class="ok-sub">File: {entry.ok.file_path}</div>
                  {/if}
                  <pre class="ok-output">{@html ansiToHtml(entry.ok.response || "")}</pre>
                </div>
              {/if}

              {#if entry.output || entry.displayOutput}
                <pre class="entry-output">{@html renderOutput(entry)}</pre>
              {/if}

              {#if entry.gridLayer}
                <div class="entry-grid">
                  <TileGrid
                    layer={entry.gridLayer}
                    selectedChar=" "
                    selectedCode={32}
                    tool="select"
                    showGrid={false}
                    showLinks={false}
                    zoom={0.6}
                    onTileChange={() => {}}
                    onTileClick={() => {}}
                  />
                </div>
              {/if}

              {#if entry.storyState}
                <div class="entry-story">
                  <div class="story-preview">
                    <StoryRenderer
                      story={entry.storyState}
                      showProgress={false}
                      theme="dark"
                      onSubmit={(answers) => submitStory(entry.id, entry.storyState, answers)}
                    />
                  </div>
                  {#if entry.storySubmitStatus}
                    <div class="text-xs text-gray-300 mt-2">{entry.storySubmitStatus}</div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        {/if}
      </div>

      <div class="ucode-input">
        <div class="helper-lines">
          <div class="helper-line">{helperLine1}</div>
          <div class="helper-line">{helperLine2}</div>
        </div>
        <div class="input-row">
          <input
            class="input-field wiz-terminal-input"
            placeholder=":STATUS, OK EXPLAIN core/tui/ucode.py, /ls"
            bind:value={commandInput}
            on:keydown={handleInputKeydown}
          />
          <TerminalButton className="send-btn" variant="accent" on:click={() => handleDispatch()}>
            Send
          </TerminalButton>
        </div>
        <div class="hint-row">
          <span>Tips: `:` command, `OK` local Vibe, `/` shell</span>
          {#if okStatus}
            <span>OK ctx {okStatus.context_window} | default {okStatus.default_model}</span>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <aside class="ucode-side">
    <section class="panel">
      <div class="panel-header">OK / Vibe</div>
      <div class="panel-body">
        {#if okStatus}
          <div class="status-row">
            <span class="label">Status</span>
            <span class={okStatus.ready ? "good" : "warn"}>
              {okStatus.ready ? "Ready" : okStatus.issue}
            </span>
          </div>
          <div class="status-row">
            <span class="label">Context</span>
            <span>{okStatus.context_window}</span>
          </div>
          <div class="status-row">
            <span class="label">Ollama</span>
            <span>{okStatus.ollama_endpoint}</span>
          </div>
          <label class="field">
            <span class="label">Local model</span>
            <select class="select wiz-terminal-input" bind:value={okModel} on:change={handleModelChange}>
              {#each okModels as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
          </label>
          <label class="field">
            <span class="label">Default profile</span>
            <select class="select wiz-terminal-input" bind:value={okProfile}>
              <option value="core">core</option>
              <option value="dev" disabled={!okStatus?.dev_mode_active}>
                dev {okStatus?.dev_mode_active ? "" : "(DEV OFF)"}
              </option>
            </select>
          </label>
          <div class="button-row">
            <button class="ghost-btn wiz-terminal-btn" on:click={handleOkSave}>Save default</button>
          </div>
          {#if okSaveStatus}
            <div class="text-xs text-gray-300">{okSaveStatus}</div>
          {/if}
          {#if !okStatus?.dev_mode_active}
            <div class="text-xs text-amber-200">Coding assistant model is locked until Dev Mode is active.</div>
          {/if}
          <div class="divider"></div>
          <label class="field">
            <span class="label">File path</span>
            <input class="input wiz-terminal-input" bind:value={okFilePath} placeholder="core/tui/ucode.py" />
          </label>
          <label class="field">
            <span class="label">Line range</span>
            <input class="input wiz-terminal-input" bind:value={okRange} placeholder="120 220 or 120:220" />
          </label>
          <div class="button-row">
            <button class="ghost-btn wiz-terminal-btn" on:click={() => setQuickOkCommand("EXPLAIN")}>EXPLAIN</button>
            <button class="ghost-btn wiz-terminal-btn" on:click={() => setQuickOkCommand("DIFF")}>DIFF</button>
            <button class="ghost-btn wiz-terminal-btn" on:click={() => setQuickOkCommand("PATCH")}>PATCH</button>
          </div>
        {:else}
          <div class="text-gray-400 text-sm">OK status unavailable.</div>
        {/if}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Command Hint</div>
      <div class="panel-body">
        {#if selectedCommand}
          <div class="status-row">
            <span class="label">Command</span>
            <span>{selectedCommand.name}</span>
          </div>
          {#if selectedCommand.help_text}
            <div class="text-gray-300 text-xs">{selectedCommand.help_text}</div>
          {/if}
          {#if selectedCommand.syntax}
            <div class="text-gray-400 text-xs font-mono">{selectedCommand.syntax}</div>
          {/if}
          {#if selectedCommand.options?.length}
            <div class="text-gray-400 text-xs">Options:</div>
            <ul class="list-disc list-inside text-xs text-gray-300">
              {#each selectedCommand.options as opt}
                <li>{opt}</li>
              {/each}
            </ul>
          {/if}
          {#if selectedCommand.examples?.length}
            <div class="text-gray-400 text-xs">Examples:</div>
            <ul class="list-disc list-inside text-xs text-gray-300">
              {#each selectedCommand.examples as ex}
                <li>{ex}</li>
              {/each}
            </ul>
          {/if}
        {:else}
          <div class="text-gray-400 text-sm">Type a command to see hints.</div>
        {/if}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Modes & Roles</div>
      <div class="panel-body">
        <div class="status-row">
          <span class="label">Current user</span>
            <span>{currentUser?.username || "-"}</span>
        </div>
        <div class="status-row">
          <span class="label">Role</span>
            <span>{currentUser?.role || "-"}</span>
        </div>
        <label class="field">
          <span class="label">Switch user</span>
          <select class="select wiz-terminal-input" on:change={handleUserSwitch}>
            <option value="">Select...</option>
            {#each userList as user}
              <option value={user.username}>{user.username} ({user.role})</option>
            {/each}
          </select>
        </label>
        <label class="field">
          <span class="label">Set role</span>
          <select class="select wiz-terminal-input" on:change={handleRoleChange}>
            <option value="">Select...</option>
            <option value="admin">admin</option>
            <option value="user">user</option>
            <option value="guest">guest</option>
          </select>
        </label>
        <button class="ghost-btn wiz-terminal-btn" on:click={handleGhostToggle}>
          {ghostMode ? "Exit Ghost Mode" : "Enter Ghost Mode"}
        </button>
        <button class="ghost-btn wiz-terminal-btn" on:click={handleSetupClick}>Setup</button>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">DEV Mode</div>
      <div class="panel-body">
        <div class="status-row">
          <span class="label">Dev state</span>
          <span>{devStatus?.active ? "ON" : "OFF"}</span>
        </div>
        {#if devRequirements}
          <div class="status-row">
            <span class="label">/dev present</span>
            <span>{devRequirements.dev_root_present ? "yes" : "no"}</span>
          </div>
          <div class="status-row">
            <span class="label">templates ok</span>
            <span>{devRequirements.dev_template_present ? "yes" : "no"}</span>
          </div>
        {/if}
        <div class="button-row">
          <button class="ghost-btn wiz-terminal-btn" disabled={!canDevMode} on:click={() => handleDevToggle(true)}>DEV ON</button>
          <button class="ghost-btn wiz-terminal-btn" disabled={!canDevMode} on:click={() => handleDevToggle(false)}>DEV OFF</button>
          <button class="ghost-btn wiz-terminal-btn" disabled={!canDevMode} on:click={handleDevRestart}>Restart</button>
        </div>
        {#if devGateError}
          <div class="text-xs text-amber-200">{devGateError}</div>
        {/if}
        {#if !canDevMode}
          <div class="text-xs text-amber-200">Dev mode requires admin role and /dev templates.</div>
        {/if}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Hotkeys</div>
      <div class="panel-body">
        <div class="hotkey-grid">
          {#each hotkeys as key}
            <button class="hotkey-btn" on:click={() => handleHotkeyClick(key.key)}>
              <span class="hotkey-label">{key.key}</span>
              <span class="hotkey-action">{key.action}</span>
            </button>
          {/each}
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Quotas</div>
      <div class="panel-body">
        {#if Object.keys(quotas).length}
          {#each Object.entries(quotas) as [provider, data]}
            <div class="quota-row">
              <div class="quota-title">{provider}</div>
              <div class="quota-detail">Today: {data.daily?.cost ?? "-"} / {data.daily?.budget ?? "-"}</div>
              <div class="quota-detail">Month: {data.monthly?.cost ?? "-"} / {data.monthly?.budget ?? "-"}</div>
            </div>
          {/each}
        {:else}
          <div class="text-gray-400 text-sm">No quota data.</div>
        {/if}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Recent OK Outputs</div>
      <div class="panel-body">
        {#if okHistory.length === 0}
          <div class="text-gray-400 text-sm">No OK outputs yet.</div>
        {:else}
          {#each okHistory.slice(0, 5) as entry}
            <div class="ok-history-item">
              <div class="ok-history-title">{entry.mode} | {entry.model}</div>
              <div class="ok-history-sub">{entry.file_path || ""}</div>
            </div>
          {/each}
        {/if}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">Live Logs</div>
      <div class="panel-body">
        <div class="field">
          <span class="label">Component</span>
          <select class="select wiz-terminal-input" bind:value={logComponent}>
            <option value="wizard">wizard</option>
            <option value="core">core</option>
            <option value="script">script</option>
            <option value="dev">dev</option>
            <option value="extension">extension</option>
          </select>
        </div>
        <div class="field">
          <span class="label">Log name</span>
          <input class="input wiz-terminal-input" bind:value={logName} placeholder="wizard-server" />
        </div>
        <div class="button-row">
          <button class="ghost-btn wiz-terminal-btn" on:click={startLogStream} disabled={logStreamActive}>
            {logStreamActive ? "Streaming..." : "Start Stream"}
          </button>
          <button class="ghost-btn wiz-terminal-btn" on:click={stopLogStream} disabled={!logStreamActive}>
            Stop
          </button>
        </div>
        {#if logStreamError}
          <div class="text-xs text-red-300 mt-2">{logStreamError}</div>
        {/if}
        <div class="log-stream wiz-terminal-log">
          {#if logEntries.length === 0}
            <div class="text-gray-400 text-xs">No log events yet.</div>
          {:else}
            {#each logEntries as line}
              <div class="log-line">{line}</div>
            {/each}
          {/if}
        </div>
      </div>
    </section>
  </aside>
</div>

<style>
  .ucode-shell {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 360px;
    gap: 1.5rem;
    padding: 1.5rem 1.5rem 120px;
    min-height: calc(
      100dvh - var(--wizard-bottom-bar-height, 52px) -
        var(--wizard-cli-bar-height, 44px) - 72px
    );
    align-items: stretch;
    overflow: hidden;
  }

  .ucode-main {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
  }

  .ucode-header {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .status-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .defaults-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 0.5rem 0.75rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(56, 189, 248, 0.35);
    background: rgba(15, 23, 42, 0.85);
    color: #e2e8f0;
  }

  .defaults-label {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #7dd3fc;
  }

  .defaults-value {
    font-family: var(--mdk-font-code);
    color: #f8fafc;
  }

  .log-stream {
    margin-top: 0.75rem;
    background: #0b1120;
    border: 1px solid rgba(51, 65, 85, 0.6);
    border-radius: 0.5rem;
    padding: 0.5rem;
    max-height: 240px;
    overflow-y: auto;
    font-family: var(--mdk-font-code);
    color: #e2e8f0;
  }

  .log-line {
    white-space: pre-wrap;
    word-break: break-word;
  }

  .chip {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
    background: rgba(30, 41, 59, 0.7);
    color: #e2e8f0;
    border: 1px solid rgba(148, 163, 184, 0.3);
  }

  .ucode-console {
    display: flex;
    flex-direction: column;
    background: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 1rem;
    overflow: hidden;
    min-height: 0;
    flex: 1;
  }

  .ucode-history {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .history-entry {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(51, 65, 85, 0.7);
    border-radius: 0.75rem;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .entry-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .entry-command {
    font-family: var(--mdk-font-code);
    color: #f8fafc;
  }

  .entry-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #94a3b8;
  }

  .status-pill {
    padding: 0.1rem 0.4rem;
    border-radius: 999px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .status-success {
    background: rgba(16, 185, 129, 0.2);
    color: #6ee7b7;
  }

  .status-error {
    background: rgba(248, 113, 113, 0.2);
    color: #fecaca;
  }

  .status-warning {
    background: rgba(251, 191, 36, 0.2);
    color: #fde68a;
  }

  .status-pending {
    background: rgba(148, 163, 184, 0.2);
    color: #e2e8f0;
  }

  .status-streaming {
    background: rgba(59, 130, 246, 0.2);
    color: #bfdbfe;
  }

  .entry-output {
    background: #0b1220;
    border-radius: 0.5rem;
    padding: 0.75rem;
    font-family: var(--mdk-font-code);
    color: #e2e8f0;
    white-space: pre-wrap;
    overflow-x: auto;
  }

  .ok-block {
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: rgba(14, 165, 233, 0.1);
  }

  .ok-title {
    font-size: 0.75rem;
    color: #bae6fd;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .ok-sub {
    font-size: 0.7rem;
    color: #7dd3fc;
  }

  .ok-output {
    margin-top: 0.5rem;
    font-family: var(--mdk-font-code);
    white-space: pre-wrap;
    color: #e0f2fe;
  }

  .entry-grid,
  .entry-story {
    margin-top: 0.5rem;
  }

  .story-preview :global(.story-renderer) {
    min-height: auto;
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 0.75rem;
    overflow: hidden;
  }

  .ucode-input {
    padding: 0.75rem 1rem 1rem;
    border-top: 1px solid #1f2937;
    background: #0b1220;
  }

  .helper-lines {
    font-family: var(--mdk-font-code);
    color: #94a3b8;
    margin-bottom: 0.5rem;
  }

  .input-row {
    display: flex;
    gap: 0.75rem;
  }

  .input-field {
    flex: 1;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.5rem;
    padding: 0.6rem 0.75rem;
    color: #f8fafc;
    font-family: var(--mdk-font-code);
  }

  .send-btn {
    background: #38bdf8;
    color: #0f172a;
    border: none;
    border-radius: 0.5rem;
    padding: 0 1rem;
    font-weight: 700;
  }

  .hint-row {
    margin-top: 0.5rem;
    display: flex;
    justify-content: space-between;
    color: #64748b;
  }

  .ucode-side {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow-y: auto;
    padding-right: 0.25rem;
    min-height: 0;
    max-height: calc(
      100dvh - var(--wizard-bottom-bar-height, 52px) -
        var(--wizard-cli-bar-height, 44px) - 96px
    );
  }

  .panel {
    background: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 0.75rem;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .panel-header {
    padding: 0.75rem 1rem;
    font-weight: 700;
    color: #f8fafc;
    border-bottom: 1px solid #1f2937;
  }

  .panel-body {
    padding: 0.75rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    color: #e2e8f0;
    min-height: 0;
    overflow: auto;
  }

  .status-row {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .label {
    color: #94a3b8;
  }

  .good {
    color: #34d399;
  }

  .warn {
    color: #facc15;
  }

  .divider {
    height: 1px;
    background: #1f2937;
    margin: 0.5rem 0;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .input,
  .select {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.4rem;
    padding: 0.4rem 0.5rem;
    color: #e2e8f0;
  }

  .button-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .ghost-btn {
    background: rgba(148, 163, 184, 0.15);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #e2e8f0;
    border-radius: 0.4rem;
    padding: 0.3rem 0.6rem;
  }

  .hotkey-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
  }

  .hotkey-btn {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.5rem;
    padding: 0.5rem;
    color: #e2e8f0;
  }

  .hotkey-label {
    font-weight: 700;
    color: #38bdf8;
  }

  .hotkey-action {
    color: #94a3b8;
  }

  .quota-row {
    padding: 0.4rem 0;
    border-bottom: 1px solid #1f2937;
  }

  .quota-row:last-child {
    border-bottom: none;
  }

  .quota-title {
    font-weight: 600;
  }

  .quota-detail {
    color: #94a3b8;
  }

  .ok-history-item {
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 0.4rem 0.5rem;
    border-radius: 0.4rem;
    background: rgba(14, 165, 233, 0.08);
  }

  .ok-history-title {
    font-weight: 600;
  }

  .ok-history-sub {
    font-size: 0.7rem;
    color: #94a3b8;
  }

  :global(.ansi-bold) {
    font-weight: 700;
  }

  :global(.ansi-dim) {
    opacity: 0.7;
  }

  :global(.ansi-red) {
    color: #f87171;
  }

  :global(.ansi-green) {
    color: #34d399;
  }

  :global(.ansi-yellow) {
    color: #facc15;
  }

  :global(.ansi-cyan) {
    color: #38bdf8;
  }

  @media (max-width: 1100px) {
    .ucode-shell {
      grid-template-columns: 1fr;
    }
  }
</style>
