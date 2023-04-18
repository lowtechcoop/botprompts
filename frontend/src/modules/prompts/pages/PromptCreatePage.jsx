import { Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import React from "react";
import { PromptsCreateEditForm } from "../forms/PromptsCreateEditForm";

export const PromptsCreatePage = () => {
    return (
        <Grid2 container sx={{ p: 2 }}>
            <Grid2 xs={12} sx={{ mb: 2 }}>
                <Typography variant="h4">Create a Prompt</Typography>
            </Grid2>
            <Grid2 xs={12}>
                <PromptsCreateEditForm />
            </Grid2>
        </Grid2>
    );
};
