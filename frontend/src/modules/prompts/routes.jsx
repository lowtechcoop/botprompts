import React from "react";
import { PromptsListPage } from "./pages/PromptListPage";
import { PromptsCreatePage } from "./pages/PromptCreatePage";
import { PromptPage } from "./pages/PromptPage";
import { PromptsEditPage } from "./pages/PromptEditPage";

export const modPromptsRoutes = [
    {
        path: "/prompts",
        element: <PromptsListPage />,
    },
    {
        path: "/prompts/new",
        element: <PromptsCreatePage />,
    },
    {
        path: "/prompts/:slug",
        element: <PromptPage />,
    },
    {
        path: "/prompts/:slug/:revision",
        element: <PromptPage />,
    },
    {
        path: "/prompts/:slug/edit",
        element: <PromptsEditPage />,
    },
];
