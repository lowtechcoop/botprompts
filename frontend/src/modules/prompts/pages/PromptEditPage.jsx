import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Loader } from "../../../components/loading/Loader";
import AppHttpError from "../../../app/AppHttpError";
import { PromptsCreateEditForm } from "../forms/PromptsCreateEditForm";
import { ApiDataProvider, DefaultListParams } from "../../../providers/api/provider";


export const PromptsEditPage = (props) => {
    const { slug } = useParams();
    const [isLoading, setIsLoading] = useState(true);
    const [prompt, setPrompt] = useState(undefined);

    useEffect(() => {
        if (undefined === prompt) {
            ApiDataProvider.getList("prompts", {
                ...DefaultListParams,
                filter: { slug: slug },
            })
                .then((resp) => {
                    if (resp.prompts.length > 0) {
                        setPrompt(resp.prompts[0]);
                    }

                    setIsLoading(false);
                })
                .catch((err) => {
                    console.log(err);
                });
        }
    });

    if (isLoading) {
        return <Loader />;
    }

    if (prompt === undefined) {
        throw new AppHttpError({ statusText: `Prompt '${slug}' not found`, status: 404 });
    }

    return (
        <Grid2 container sx={{ p: 2 }}>
            <Grid2 xs={12} sx={{ mb: 2 }}>
                <Typography variant="h4">Edit Prompt</Typography>
            </Grid2>
            <Grid2 xs={12}>
                <PromptsCreateEditForm prompt={prompt} />
            </Grid2>
        </Grid2>
    );
};
