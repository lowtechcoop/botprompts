import { RouterProvider } from "react-router-dom";
import { getUnauthenticatedRouter } from "./routes";
import { ThemeProvider, createTheme } from "@mui/material";

const mdTheme = createTheme();

export const AppUnauthenticated = (props) => {
    return (
        <ThemeProvider theme={mdTheme}>
            <RouterProvider router={getUnauthenticatedRouter(props)} />
        </ThemeProvider>
    );
};
