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

import { auth } from "@/app/(auth)/auth";
import { createBackendClient } from "@/lib/backend-client";
import { ChatSDKError } from "@/lib/errors";

export const maxDuration = 60;

export async function POST(request: Request) {
  try {
    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError("unauthorized:chat").toResponse();
    }

    const body = await request.json();
    const { id, message, selectedChatModel, selectedVisibilityType } = body;

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

    // Create streaming response
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        try {
          // Stream from Python backend
          for await (const chunk of backendClient.streamChat(chatRequest)) {
            // Forward SSE events to client
            const data = `data: ${JSON.stringify(chunk)}\n\n`;
            controller.enqueue(encoder.encode(data));
          }
        } catch (error) {
          console.error("Streaming error:", error);
          const errorData = {
            type: "error",
            error: error instanceof Error ? error.message : "Unknown error",
          };
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(errorData)}\n\n`));
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
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
    const backendClient = createBackendClient(session.user.id);
    await backendClient.deleteChat(id);

    return Response.json({ success: true, id }, { status: 200 });
  } catch (error) {
    console.error("Delete chat error:", error);
    return new ChatSDKError("offline:chat").toResponse();
  }
}

