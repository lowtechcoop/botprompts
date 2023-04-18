import { Box, Container, Paper } from "@mui/material";
import { BPAppBar } from "../components/appbar/BPAppBar";

const BasePage = ({ contentPane }) => {
    return (
        <>
            <Paper>
                <Box sx={{ display: "flex" }}>
                    <BPAppBar></BPAppBar>
                </Box>
                <Container maxWidth="xl">{contentPane}</Container>
            </Paper>
        </>
    );
};
export default BasePage;
