export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export async function fetchAgents() {
  try {
    const res = await fetch(`${API_BASE_URL}/agents`);
    if (!res.ok) throw new Error("Failed to fetch agents");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
}

export async function fetchTasks() {
  try {
    const res = await fetch(`${API_BASE_URL}/tasks`);
    if (!res.ok) throw new Error("Failed to fetch tasks");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
}

export async function fetchLogs() {
  try {
    const res = await fetch(`${API_BASE_URL}/logs`);
    if (!res.ok) throw new Error("Failed to fetch logs");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch (error) {
    return false;
  }
}

export async function sendCommand(command: string) {
    // Determine type of command
    // Simple parsing for demo
    // e.g. "build user profile" -> POST /execute
    
    // For now, just log it locally or implement a simple /execute proxy
    // If the command starts with "run: ", we treat it as a task description
    if (command.startsWith("run: ") || command.startsWith("build ") || command.startsWith("create ")) {
        const description = command.replace("run: ", "");
        try {
            const res = await fetch(`${API_BASE_URL}/execute`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task: {
                        id: `cmd-${Date.now()}`,
                        type: "user_command",
                        description: description,
                        requires_approval: true
                    }
                })
            });
            return await res.json();
        } catch (error) {
            console.error("Command failed", error);
            return { status: "error", message: String(error) };
        }
    }
    
    return { status: "ignored", message: "Command not recognized (try 'run: ...')" };
}

export async function fetchSystemHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/system/health`);
    if (!res.ok) throw new Error("Failed to fetch system health");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return null;
  }
}

export async function respondToApproval(approvalId: string, status: "approved" | "rejected") {
    try {
        const res = await fetch(`${API_BASE_URL}/approvals/respond`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                approval_id: approvalId,
                status: status,
                timestamp: new Date().toISOString()
            })
        });
        return await res.json();
    } catch (error) {
        console.error("Approval response failed", error);
        return { status: "error", message: String(error) };
    }
}
