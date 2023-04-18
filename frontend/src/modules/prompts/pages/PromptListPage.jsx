import {
    Box,
    Button,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Add } from "@mui/icons-material";
import { ApiDataProvider } from "../../../providers/api/provider";
import AppHttpError from "../../../app/AppHttpError";
import { Loader } from "../../../components/loading/Loader";
import { DateTime } from "luxon";

const PromptsList = ({ prompts }) => {
    const navigate = useNavigate();
    const handlePromptSelected = (e, slug, prompt) => {
        navigate(`/prompts/${slug}`, { state: { prompt: prompt } });
    };

    const heading = (
        <TableRow>
            <TableCell sx={{ width: "2em" }}>ID</TableCell>
            <TableCell sx={{ width: "5em" }}>Name</TableCell>
            <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>Description</TableCell>
            <TableCell>Last updated</TableCell>
        </TableRow>
    );

    const rows = prompts.map((p) => (
        <TableRow key={p.id} hover onClick={(event) => handlePromptSelected(event, p.slug, p)}>
            <TableCell>{p.id}</TableCell>
            <TableCell>{p.slug}</TableCell>
            <TableCell sx={{ display: { xs: "none", sm: "table-cell" } }}>
                {p.description}
            </TableCell>
            <TableCell>
                <Box component="span" data-timestamp={p.updated_at}>
                    {DateTime.fromISO(p.updated_at).toRelative()}
                </Box>
            </TableCell>
        </TableRow>
    ));

    return (
        <>
            <Grid2 container sx={{ p: 2 }}>
                <Grid2 xs={12} sx={{ mb: 2 }}>
                    <Typography variant="h4">Prompts</Typography>
                </Grid2>
                <Grid2 xs={12}>
                    <Box>
                        <TableContainer component={Paper}>
                            <Table>
                                <TableHead>{heading}</TableHead>
                                <TableBody>{rows}</TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                </Grid2>
            </Grid2>
        </>
    );
};

export const PromptsListPage = (props) => {
    const [isLoading, setIsLoading] = useState(true);
    const [prompts, setPrompts] = useState(undefined);

    useEffect(() => {
        if (undefined === prompts) {
            ApiDataProvider.getCurrentPromptsList().then((resp) => {
                setPrompts(resp.prompts);
                setIsLoading(false);
            });
        }
    }, [prompts]);

    if (isLoading) {
        return <Loader />;
    }

    if (undefined === prompts) {
        throw new AppHttpError({ statusText: `Could not load prompts.`, status: 404 });
    }

    return (
        <Box>
            <Grid2 container>
                <Grid2 xs={12}>
                    <PromptsList prompts={prompts} />
                </Grid2>
            </Grid2>
            <Grid2 container justifyContent="end">
                <Grid2 sx={{ mt: 1, mb: 4, p: 2 }}>
                    <Button variant="outlined" href="/prompts/new">
                        <Add /> Create New Prompt
                    </Button>
                </Grid2>
            </Grid2>
        </Box>
    );
};
