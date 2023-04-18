import { Navigate } from "react-router-dom";

export const modDashboardRoutes = [
    {
        path: "/",
        element: <Navigate to="/prompts" />,
    },

];
