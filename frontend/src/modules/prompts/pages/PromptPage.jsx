import { Box, Button, Chip, Divider, Stack, Tooltip, Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { DateTime } from "luxon";
import React, { useEffect, useState } from "react";
import { ChevronLeft, Edit } from "@mui/icons-material";
import { Loader } from "../../../components/loading/Loader";
import AppHttpError from "../../../app/AppHttpError";
import { RevisionPanel } from "../panels/RevisionPanel";
import { ApiDataProvider, DefaultListParams } from "../../../providers/api/provider";
import { useParams } from "react-router-dom";

const PromptRevisionsPane = ({ prompt, revision }) => {
    if (undefined === prompt.history) {
        return <Loader />;
    }

    let revisions = prompt.history.map((r) => {
        const labelText = (
            <>
                <Box component="strong">Rev #{r.id}</Box> &bull;{" "}
                <Box component="span" data-timestamp={r.created_at}>
                    {DateTime.fromISO(r.created_at).toRelative()}
                </Box>
            </>
        );

        let styleOutline = "outlined";
        if (r.id === revision || (isNaN(revision) && r.is_current)) {
            styleOutline = "filled";
        }

        return (
            <Tooltip
                key={r.id}
                title={`${DateTime.fromISO(r.created_at).toFormat("yyyy-MM-dd HH:mm:ss")} UTC`}
                arrow
                placement="left"
                sx={{ mt: 1 }}
            >
                <Chip
                    variant={styleOutline}
                    component="a"
                    clickable
                    label={labelText}
                    href={`/prompts/${prompt.slug}/${r.id}`}
                />
            </Tooltip>
        );
    });

    return (
        <Grid2 container sx={{ mt: 3, width: "100%" }}>
            <Grid2 xs={12}>
                <Typography variant="h6">Revisions</Typography>
                <Divider />
                <Stack sx={{ mt: 1 }}>{revisions}</Stack>
            </Grid2>
        </Grid2>
    );
};

export const PromptPage = (props) => {
    const { slug, revision } = useParams();
    const [isLoading, setIsLoading] = useState(true);
    const [prompt, setPrompt] = useState(undefined);
    const [revisionContent, setRevisionContent] = useState(undefined);

    useEffect(() => {
        if (undefined === prompt) {
            ApiDataProvider.getList("prompts", {
                ...DefaultListParams,
                filter: { slug: slug },
                history: true,
            })
                .then((resp) => {
                    if (resp.prompts.length > 0) {
                        setPrompt(resp.prompts[0]);

                        if (revision !== undefined) {
                            setRevisionContent(
                                resp.prompts[0].history
                                    .filter((r) => r.id === parseInt(revision))
                                    .pop()
                            );
                        } else {
                            setRevisionContent(resp.prompts[0].revision);
                        }
                    }

                    setIsLoading(false);
                })
                .catch((err) => {
                    console.log(err);
                });
        }
    }, [prompt, revision, slug]);

    if (isLoading) {
        return <Loader />;
    }

    if (undefined === prompt) {
        throw new AppHttpError({ statusText: `Prompt '${slug}' not found`, status: 404 });
    }

    return (
        <Grid2 container>
            <Grid2 sx={{ mb: 0, pt: 3, pl: 2 }} xs={12}>
                <Typography variant="h4">
                    <Box component="em">{prompt.slug}</Box>
                </Typography>
            </Grid2>

            <Grid2 container xs={12} lg={9} sx={{ p: 2 }}>
                <Grid2 xs={12}>
                    {/* <PromptContentPane prompt={prompt} /> */}
                    <RevisionPanel revisionContent={revisionContent} />
                </Grid2>
            </Grid2>

            <Grid2 container xs={12} lg={3} sx={{ p: 2 }}>
                <PromptRevisionsPane prompt={prompt} revision={parseInt(revision)} />
            </Grid2>
            <Grid2 container justifyContent="end" xs={12} lg={9}>
                <Grid2 sx={{ mt: 1, mb: 4, p: 2 }}>
                    <Button variant="outlined" href={`/prompts`}>
                        <ChevronLeft /> Back
                    </Button>
                </Grid2>
                <Grid2 sx={{ mt: 1, mb: 4, p: 2 }}>
                    <Button variant="outlined" href={`/prompts/${slug}/edit`}>
                        <Edit /> Edit
                    </Button>
                </Grid2>
            </Grid2>
        </Grid2>
    );
};
