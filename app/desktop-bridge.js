(function () {
  function getTauriInvoke() {
    return window.__TAURI__?.core?.invoke;
  }

  function isTauriDesktop() {
    return typeof getTauriInvoke() === "function";
  }

  async function notifyAppReady() {
    const invoke = getTauriInvoke();
    if (typeof invoke !== "function") {
      return false;
    }

    await invoke("app_ready");
    return true;
  }

  async function savePdfWithDialog(defaultFileName, bytes) {
    const invoke = getTauriInvoke();
    if (typeof invoke !== "function") {
      return undefined;
    }

    const selectedPath = await invoke("plugin:dialog|save", {
      options: {
        defaultPath: defaultFileName,
        filters: [
          {
            name: "PDF",
            extensions: ["pdf"],
          },
        ],
      },
    });

    if (!selectedPath) {
      return null;
    }

    await invoke("save_pdf_file", {
      path: selectedPath,
      bytes: Array.from(bytes),
    });

    return selectedPath;
  }

  window.staarDesktopBridge = {
    ...(window.staarDesktopBridge || {}),
    isTauriDesktop,
    notifyAppReady,
    savePdfWithDialog,
  };

  if (window.location.protocol === "tauri:") {
    return;
  }

  const heartbeatPath = "/__heartbeat__";
  const shutdownPath = "/__shutdown__";
  const heartbeatIntervalMs = 30000;
  let heartbeatTimer = null;

  async function pingHeartbeat() {
    try {
      await fetch(heartbeatPath, {
        method: "HEAD",
        cache: "no-store",
      });
    } catch (error) {
      // Ignore heartbeat failures outside the desktop launcher.
    }
  }

  function notifyShutdown() {
    if (!navigator.sendBeacon) {
      return;
    }

    try {
      navigator.sendBeacon(shutdownPath, "");
    } catch (error) {
      // Ignore shutdown signaling failures outside the desktop launcher.
    }
  }

  async function enableDesktopBridge() {
    try {
      const response = await fetch(heartbeatPath, {
        method: "HEAD",
        cache: "no-store",
      });

      if (!response.ok) {
        return;
      }

      await pingHeartbeat();
      heartbeatTimer = window.setInterval(pingHeartbeat, heartbeatIntervalMs);

      window.addEventListener("pagehide", notifyShutdown);
      window.addEventListener("beforeunload", notifyShutdown);
      document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") {
          void pingHeartbeat();
        }
      });
    } catch (error) {
      // Running under a normal static file server should stay silent.
    }
  }

  void enableDesktopBridge();
})();
