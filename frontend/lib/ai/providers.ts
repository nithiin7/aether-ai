import { customProvider } from "ai";
import { isTestEnvironment } from "../constants";

// Backend-compatible provider for Ollama models
// Note: Actual model inference happens in Python backend
// This provider is only used for frontend compatibility
const createBackendProvider = () => {
  const {
    artifactModel,
    chatModel,
    reasoningModel,
    titleModel,
  } = require("./models.mock");
  
  return customProvider({
    languageModels: {
      // Legacy model IDs (for backward compatibility)
      "chat-model": chatModel,
      "chat-model-reasoning": reasoningModel,
      "title-model": titleModel,
      "artifact-model": artifactModel,
      
      // Ollama model IDs
      "phi3:mini": chatModel,
      "llama3.2:3b": chatModel,
      "llama3.2:11b-vision": chatModel,
      "qwen2.5:7b": chatModel,
      "mixtral:8x7b": chatModel,
    },
  });
};

export const myProvider = createBackendProvider();
