import React from "react";
import { createBrowserRouter } from "react-router-dom";

import RootPage from "./RootPage";
import ErrorPage from "./ErrorPage";
import { modPromptsRoutes } from "../modules/prompts/routes";
import { modDashboardRoutes } from "../modules/dashboard/routes";

export function getUnauthenticatedRouter(props) {
    return createBrowserRouter([
        {
            path: "/",
            element: <RootPage {...props} />,
            errorElement: <ErrorPage />,
            children: [...modDashboardRoutes, ...modPromptsRoutes],
        },
    ]);
}
