export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// --- CORE API TYPES ---
export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: "admin" | "developer" | "viewer";
  is_active: boolean;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: "active" | "archived" | "draft";
  owner_id: number;
}

// --- AUTHENTICATION ---
export async function login(username: string, password: string): Promise<{ access_token: string; token_type: string } | null> {
  try {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch(`${API_BASE_URL}/auth/login/access-token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (!res.ok) throw new Error("Login failed");
    return await res.json();
  } catch (error) {
    console.error("Auth Error:", error);
    return null;
  }
}

// --- AGENT ORCHESTRATION ---
export async function fetchAgents() {
  // ... (Existing implementation for Orchestrator, usually on port 8081 or proxied)
  // For now, assuming orchestrator is proxied or we point to it directly
  // TODO: Unify Orchestrator API under Core API Gateway
  try {
    const res = await fetch(`http://localhost:8081/agents`); 
    if (!res.ok) throw new Error("Failed to fetch agents");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
}

// --- PROJECTS ---
export async function fetchProjects(token: string): Promise<Project[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to fetch projects");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
}

// ... (Rest of existing functions)

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

export async function createTask(task: any) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
  try {
    const res = await fetch(`${API_BASE_URL}/tasks/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error("Failed to create task");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

export async function getTask(id: number) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
  try {
    const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) throw new Error("Failed to fetch task");
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
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
