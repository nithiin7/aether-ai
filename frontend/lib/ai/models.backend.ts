/**
 * Model definitions - Python backend version
 * 
 * This file provides an alternative implementation that fetches models
 * from the Python backend instead of using hardcoded Grok models.
 * 
 * To use this version:
 * 1. Rename this file to models.ts (backup the original first)
 * 2. Update components to use dynamic model loading
 */

import { createBackendClient } from "@/lib/backend-client";

export const DEFAULT_CHAT_MODEL: string = "phi3:mini";

export type ChatModel = {
  id: string;
  name: string;
  description: string;
  size?: string;
  capabilities?: string[];
};

// Cache for models
let cachedModels: ChatModel[] | null = null;
let lastFetch: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch available models from Python backend.
 */
export async function fetchChatModels(): Promise<ChatModel[]> {
  // Return cached models if still valid
  const now = Date.now();
  if (cachedModels && (now - lastFetch) < CACHE_DURATION) {
    return cachedModels;
  }

  try {
    const backendClient = createBackendClient();
    const models = await backendClient.getModels();
    
    cachedModels = models;
    lastFetch = now;
    
    return models;
  } catch (error) {
    console.error("Failed to fetch models from backend:", error);
    
    // Return fallback models
    return [
      {
        id: "phi3:mini",
        name: "Phi-3 Mini",
        description: "Fast 3.8B model for testing and quick responses",
        size: "3.8B",
        capabilities: ["chat", "text"],
      },
    ];
  }
}

/**
 * Get chat models synchronously (uses cached data).
 * For initial load, call fetchChatModels() first.
 */
export function getChatModels(): ChatModel[] {
  return cachedModels || [
    {
      id: "phi3:mini",
      name: "Phi-3 Mini",
      description: "Fast 3.8B model for testing and quick responses",
      size: "3.8B",
      capabilities: ["chat", "text"],
    },
  ];
}

/**
 * Alias for backward compatibility.
 */
export const chatModels = getChatModels();

/**
 * Invalidate model cache to force refresh.
 */
export function invalidateModelCache(): void {
  cachedModels = null;
  lastFetch = 0;
}

