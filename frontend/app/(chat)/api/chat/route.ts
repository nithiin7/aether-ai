/**
 * Chat API route - Python backend proxy version
 * 
 * This file provides an alternative implementation that proxies requests
 * to the Python Flask backend instead of using Vercel AI SDK directly.
 * 
 * To use this version:
 * 1. Rename this file to route.ts (backup the original first)
 * 2. Ensure Python backend is running at NEXT_PUBLIC_BACKEND_URL
 * 3. Set BACKEND_API_KEY in environment variables
 */

import { createUIMessageStream, JsonToSseTransformStream } from "ai";
import { auth } from "@/app/(auth)/auth";
import { createBackendClient } from "@/lib/backend-client";
import { deleteChatById, getChatById, saveChat, saveMessages } from "@/lib/db/queries";
import { ChatSDKError } from "@/lib/errors";
import type { ChatMessage } from "@/lib/types";
import { generateUUID } from "@/lib/utils";

export const maxDuration = 60;

export async function POST(request: Request) {
  try {
    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError("unauthorized:chat").toResponse();
    }

    const body = await request.json();
    const { id, message, selectedChatModel, selectedVisibilityType } = body;

    // Check if chat exists in frontend database, create if not
    let frontendChat = await getChatById({ id });
    if (!frontendChat) {
      // Generate a simple title from the first message
      const userText = message.parts
        ?.find((part: any) => part.type === "text")
        ?.text?.slice(0, 50) || "New Chat";
      const title = userText.length > 50 ? `${userText}...` : userText;
      
      try {
        await saveChat({
          id,
          userId: session.user.id,
          title,
          visibility: selectedVisibilityType,
        });
      } catch (error) {
        // Chat might have been created by another request, ignore
        console.warn("Failed to save chat (might already exist):", error);
      }
    } else {
      // Verify ownership
      if (frontendChat.userId !== session.user.id) {
        return new ChatSDKError("forbidden:chat").toResponse();
      }
    }

    // Create backend client with session
    const backendClient = createBackendClient(session.user.id);

    // Forward request to Python backend with streaming
    const chatRequest = {
      chat_id: id,
      message: {
        id: message.id,
        role: message.role,
        parts: message.parts,
        attachments: message.attachments || [],
      },
      model_id: selectedChatModel,
      visibility: selectedVisibilityType,
    };

    // Save user message to frontend database before streaming
    try {
      await saveMessages({
        messages: [
          {
            chatId: id,
            id: message.id,
            role: message.role,
            parts: message.parts,
            attachments: message.attachments || [],
            createdAt: new Date(),
          },
        ],
      });
    } catch (error) {
      // Ignore duplicate key errors (message might already exist)
      console.warn("Failed to save user message (might already exist):", error);
    }

    // Create UI message stream and transform backend events
    const stream = createUIMessageStream<ChatMessage>({
      execute: async ({ writer: dataStream }) => {
        let assistantMessageId: string | undefined;
        try {
          for await (const chunk of backendClient.streamChat(chatRequest)) {
            if (chunk.type === "message-start") {
              // Store message ID and write text-start
              assistantMessageId = chunk.id;
              dataStream.write({
                type: "text-start",
                id: chunk.id,
              });
            } else if (chunk.type === "text-delta") {
              // Write text delta with message ID
              if (assistantMessageId) {
                dataStream.write({
                  type: "text-delta",
                  id: assistantMessageId,
                  delta: chunk.content,
                });
              }
            } else if (chunk.type === "message-finish") {
              // Write text-end and finish
              if (assistantMessageId) {
                dataStream.write({
                  type: "text-end",
                  id: assistantMessageId,
                });
              }
              dataStream.write({
                type: "finish",
              });
            } else if (chunk.type === "error") {
              // Write error
              dataStream.write({
                type: "error",
                error: chunk.error || "Unknown error",
              });
            }
          }
        } catch (error) {
          console.error("Backend stream error:", error);
          dataStream.write({
            type: "error",
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      },
      generateId: generateUUID,
      onFinish: async ({ messages }) => {
        // Save messages to frontend database for history
        const assistantMessages = messages.filter((msg) => msg.role === "assistant");
        if (assistantMessages.length > 0) {
          try {
            await saveMessages({
              messages: assistantMessages.map((currentMessage) => ({
                id: currentMessage.id,
                role: currentMessage.role,
                parts: currentMessage.parts,
                createdAt: new Date(),
                attachments: [],
                chatId: id,
              })),
            });
          } catch (error) {
            // Ignore duplicate key errors (message might already exist)
            console.warn("Failed to save assistant message (might already exist):", error);
          }
        }
      },
      onError: () => {
        return "Oops, an error occurred!";
      },
    });

    return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }

    console.error("Unhandled error in chat API:", error);
    return new ChatSDKError("offline:chat").toResponse();
  }
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) {
    return new ChatSDKError("bad_request:api").toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError("unauthorized:chat").toResponse();
  }

  try {
    // Verify ownership before deleting
    const frontendChat = await getChatById({ id });
    if (frontendChat && frontendChat.userId !== session.user.id) {
      return new ChatSDKError("forbidden:chat").toResponse();
    }

    // Delete from backend
    const backendClient = createBackendClient(session.user.id);
    await backendClient.deleteChat(id);

    // Delete from frontend database
    if (frontendChat) {
      await deleteChatById({ id });
    }

    return Response.json({ success: true, id }, { status: 200 });
  } catch (error) {
    console.error("Delete chat error:", error);
    return new ChatSDKError("offline:chat").toResponse();
  }
}

