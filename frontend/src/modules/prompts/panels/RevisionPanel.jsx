import { Box, Divider, Paper, Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Loader } from "../../../components/loading/Loader";

export const RevisionPanel = ({ revisionContent }) => {
    const rowStyle = { mb: 2, pt: 3 };

    if(undefined===revisionContent) {
        return <Loader />;
    }

    return (
        <Grid2 container>
            <Grid2 sx={rowStyle} xs={12}>
                <Typography variant="h6">Description</Typography>
                <Divider sx={{ mb: 3 }} />
                <Typography variant="body1">{revisionContent.description}</Typography>
            </Grid2>
            <Grid2 sx={rowStyle} xs={12}>
                <Typography variant="h6" sx={{ mt: 0 }}>
                    Prompt Text
                </Typography>
                <Box
                    display="flex"
                    justifyContent="flex-end"
                    component="div"
                    sx={{
                        marginTop: "-1rem",
                        fontSize: "0.65rem",
                    }}
                >
                    {revisionContent.prompt_text.length} chars
                </Box>
                <Divider sx={{ mb: 3 }} />

                <Paper elevation={4} sx={{ p: 2 }}>
                    <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                        {revisionContent.prompt_text}
                    </Typography>
                </Paper>
            </Grid2>
        </Grid2>
    );
};
