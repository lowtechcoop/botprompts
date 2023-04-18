import React from "react";
import { AppAuthenticated } from "./app/AppAuthenticated";
import { AppUnauthenticated } from "./app/AppUnauthenticated";
import { AppLoading } from "./components/loading/AppLoading";
import { Box } from "@mui/material";
import "./App.css";

function App() {
    const loggedIn = false;

    return (
        <Box sx={{ backgroundColor: "text.secondary", height: "100vh" }}>
            <React.Suspense fallback={<AppLoading />}>
                {loggedIn ? <AppAuthenticated /> : <AppUnauthenticated />}
            </React.Suspense>
        </Box>
    );
}

export default App;
