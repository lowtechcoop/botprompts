import { Box, Card, CardContent, Paper, Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import React from "react";

export const AppLoading = () => {
    return (
        <>
            <Grid2
                container
                component="main"
                spacing={2}
                justifyContent="center"
                sx={{ height: "100vh", align: "center" }}
            >
                <Box component="section">
                    <Paper>
                        <Card sx={{ mt: 10, p: 4, minWidth: 100 }}>
                            <CardContent>
                                <Typography variant="h5">Loading...</Typography>
                            </CardContent>
                        </Card>
                    </Paper>
                </Box>
            </Grid2>
        </>
    );
};
