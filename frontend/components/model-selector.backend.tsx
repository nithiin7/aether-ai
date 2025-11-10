"use client";

/**
 * Model selector component - Python backend version
 * 
 * This component fetches available models from the Python backend
 * instead of using hardcoded models.
 * 
 * To use this version:
 * 1. Rename this file to model-selector.tsx (backup the original first)
 * 2. Ensure the backend is running and accessible
 */

import type { Session } from "next-auth";
import { startTransition, useEffect, useMemo, useOptimistic, useState } from "react";
import { saveChatModelAsCookie } from "@/app/(chat)/actions";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { BackendModel } from "@/lib/backend-client";
import { createBackendClient } from "@/lib/backend-client";
import { cn } from "@/lib/utils";
import { CheckCircleFillIcon, ChevronDownIcon } from "./icons";

export function ModelSelector({
  session,
  selectedModelId,
  className,
}: {
  session: Session;
  selectedModelId: string;
} & React.ComponentProps<typeof Button>) {
  const [open, setOpen] = useState(false);
  const [optimisticModelId, setOptimisticModelId] = useOptimistic(selectedModelId);
  const [models, setModels] = useState<BackendModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch models from backend on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const backendClient = createBackendClient();
        const fetchedModels = await backendClient.getModels();
        setModels(fetchedModels);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch models:", err);
        setError("Failed to load models");
        // Set fallback model
        setModels([
          {
            id: "phi3:mini",
            name: "Phi-3 Mini",
            description: "Fast 3.8B model for testing and quick responses",
            size: "3.8B",
            capabilities: ["chat", "text"],
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  const selectedModel = useMemo(
    () => models.find((model) => model.id === optimisticModelId),
    [optimisticModelId, models]
  );

  if (loading) {
    return (
      <Button className="md:h-[34px] md:px-2" variant="outline" disabled>
        Loading models...
      </Button>
    );
  }

  if (error) {
    return (
      <Button className="md:h-[34px] md:px-2" variant="outline" disabled>
        {error}
      </Button>
    );
  }

  return (
    <DropdownMenu onOpenChange={setOpen} open={open}>
      <DropdownMenuTrigger
        asChild
        className={cn(
          "w-fit data-[state=open]:bg-accent data-[state=open]:text-accent-foreground",
          className
        )}
      >
        <Button
          className="md:h-[34px] md:px-2"
          data-testid="model-selector"
          variant="outline"
        >
          {selectedModel?.name || selectedModelId}
          <ChevronDownIcon />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="start"
        className="min-w-[280px] max-w-[90vw] sm:min-w-[300px]"
      >
        {models.map((model) => {
          const { id } = model;

          return (
            <DropdownMenuItem
              asChild
              data-active={id === optimisticModelId}
              data-testid={`model-selector-item-${id}`}
              key={id}
              onSelect={() => {
                setOpen(false);

                startTransition(() => {
                  setOptimisticModelId(id);
                  saveChatModelAsCookie(id);
                });
              }}
            >
              <button
                className="group/item flex w-full flex-row items-center justify-between gap-2 sm:gap-4"
                type="button"
              >
                <div className="flex flex-col items-start gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm sm:text-base">{model.name}</span>
                    {model.size && (
                      <span className="text-xs text-muted-foreground">
                        ({model.size})
                      </span>
                    )}
                  </div>
                  <div className="line-clamp-2 text-muted-foreground text-xs">
                    {model.description}
                  </div>
                  {model.capabilities && model.capabilities.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {model.capabilities.map((cap) => (
                        <span
                          key={cap}
                          className="text-xs bg-muted px-1.5 py-0.5 rounded"
                        >
                          {cap}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="shrink-0 text-foreground opacity-0 group-data-[active=true]/item:opacity-100 dark:text-foreground">
                  <CheckCircleFillIcon />
                </div>
              </button>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

