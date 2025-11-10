/**
 * Backend API client for Python Flask backend.
 * Handles SSE streaming and typed API calls.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5001";
const BACKEND_API_KEY = process.env.BACKEND_API_KEY || "shared-secret-between-frontend-and-backend";

export interface BackendModel {
  id: string;
  name: string;
  description: string;
  size: string;
  capabilities: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  parts: Array<{
    type: string;
    text?: string;
    [key: string]: any;
  }>;
  attachments?: any[];
}

export interface ChatRequest {
  chat_id?: string;
  message: ChatMessage;
  model_id: string;
  system_prompt?: string;
  visibility?: "public" | "private";
}

export interface SSEMessage {
  type: string;
  [key: string]: any;
}

/**
 * Get authentication headers for backend requests.
 */
function getAuthHeaders(userId?: string): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    "X-API-Key": BACKEND_API_KEY,
  };

  // Pass user ID in header (backend expects this for auth)
  if (userId) {
    headers["X-User-Id"] = userId;
  }

  return headers;
}

/**
 * Backend API client class.
 */
export class BackendClient {
  private baseURL: string;
  private userId?: string;

  constructor(userId?: string) {
    this.baseURL = BACKEND_URL;
    this.userId = userId;
  }

  /**
   * Health check.
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/health`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get available models.
   */
  async getModels(): Promise<BackendModel[]> {
    const response = await fetch(`${this.baseURL}/api/health/models`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`);
    }

    const data = await response.json();
    return data.models;
  }

  /**
   * Stream chat response using SSE.
   */
  async *streamChat(request: ChatRequest): AsyncGenerator<SSEMessage> {
    const response = await fetch(`${this.baseURL}/api/chat`, {
      method: "POST",
      headers: getAuthHeaders(this.userId),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("No response body");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data;
            } catch (e) {
              console.error("Failed to parse SSE data:", e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Delete a chat.
   */
  async deleteChat(chatId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/chat?id=${chatId}`, {
      method: "DELETE",
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete chat: ${response.statusText}`);
    }
  }

  /**
   * Get chat messages.
   */
  async getChatMessages(chatId: string): Promise<ChatMessage[]> {
    const response = await fetch(`${this.baseURL}/api/chat/${chatId}/messages`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.statusText}`);
    }

    const data = await response.json();
    return data.messages;
  }

  /**
   * Get user's chat history.
   */
  async getChatHistory(): Promise<any[]> {
    const response = await fetch(`${this.baseURL}/api/history`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to get history: ${response.statusText}`);
    }

    const data = await response.json();
    return data.chats;
  }

  /**
   * Create a document.
   */
  async createDocument(
    title: string,
    content: string = "",
    kind: "text" | "code" | "image" | "sheet" = "text"
  ): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/document`, {
      method: "POST",
      headers: getAuthHeaders(this.userId),
      body: JSON.stringify({ title, content, kind }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create document: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get a document.
   */
  async getDocument(documentId: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/document/${documentId}`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to get document: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update a document.
   */
  async updateDocument(documentId: string, content: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/document/${documentId}`, {
      method: "PUT",
      headers: getAuthHeaders(this.userId),
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update document: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a document.
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/document/${documentId}`, {
      method: "DELETE",
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete document: ${response.statusText}`);
    }
  }

  /**
   * List user's documents.
   */
  async listDocuments(kind?: string, limit: number = 50): Promise<any[]> {
    const params = new URLSearchParams();
    if (kind) params.append("kind", kind);
    params.append("limit", limit.toString());

    const response = await fetch(`${this.baseURL}/api/document?${params}`, {
      headers: getAuthHeaders(this.userId),
    });

    if (!response.ok) {
      throw new Error(`Failed to list documents: ${response.statusText}`);
    }

    const data = await response.json();
    return data.documents;
  }

  /**
   * Get document suggestions.
   */
  async getDocumentSuggestions(
    documentId: string,
    includeResolved: boolean = false
  ): Promise<any[]> {
    const params = new URLSearchParams();
    params.append("include_resolved", includeResolved.toString());

    const response = await fetch(
      `${this.baseURL}/api/suggestions/${documentId}?${params}`,
      {
        headers: getAuthHeaders(this.userId),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get suggestions: ${response.statusText}`);
    }

    const data = await response.json();
    return data.suggestions;
  }

  /**
   * Resolve a suggestion.
   */
  async resolveSuggestion(suggestionId: string): Promise<void> {
    const response = await fetch(
      `${this.baseURL}/api/suggestions/${suggestionId}/resolve`,
      {
        method: "POST",
        headers: getAuthHeaders(this.userId),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to resolve suggestion: ${response.statusText}`);
    }
  }
}

/**
 * Create a backend client instance.
 */
export function createBackendClient(userId?: string): BackendClient {
  return new BackendClient(userId);
}

