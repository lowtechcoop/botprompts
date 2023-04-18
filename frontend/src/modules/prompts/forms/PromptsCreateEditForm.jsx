import { Box, Button } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import React, { useState } from "react";
import { Form, useNavigate } from "react-router-dom";
import { Add, Check, ChevronLeft } from "@mui/icons-material";
import ConstrainedInput from "../../../components/input/ConstrainedInput";
import { ApiDataProvider, DefaultListParams } from "../../../providers/api/provider";
import slugify from "slugify"

export const PromptsCreateEditForm = ({ prompt }) => {
    const alertOffset = 10; // Number of characters before the end of the max length before the colour turns
    const maxLengths = { slug: 64, description: 4096, prompt_text: 4096 };
    const stateDict = { slug: "", description: "", prompt_text: "" };

    const navigate = useNavigate();
    const [form, setForm] = useState({
        slug: prompt ? prompt.slug : "",
        description: prompt ? prompt.revision.description : "",
        prompt_text: prompt ? prompt.revision.prompt_text : "",
    });
    const [formErrors, setFormErrors] = useState({ ...stateDict });

    const [isFormSubmitted, setIsFormSubmitted] = useState(false);

    const [adornmentText, setAdornmentText] = useState({ ...stateDict });
    const [adornmentStyles, setAdornmentStyles] = useState({
        slug: { color: "rgb(0,0,0)" },
        description: { color: "rgb(0,0,0)" },
        prompt_text: { color: "rgb(0,0,0)" },
    });

    const handleKeyDown = (e) => {
        const charCode = String.fromCharCode(e.which).toLowerCase();
        // Handle Ctrl+s use case
        if ((e.ctrlKey || e.metaKey) && charCode === "s") {
            e.preventDefault();
            doSubmit();
        }
    };

    const onChangeSlug = (e) => {
        // Change colours
        if (e.target.value.length >= maxLengths.slug - alertOffset) {
            setAdornmentStyles({ ...adornmentStyles, slug: { color: "error.main" } });
        } else {
            setAdornmentStyles({ ...adornmentStyles, slug: { color: "text.primary" } });
        }

        // Only allow updates to the slug when prompt is undefined (create use case)
        if (e.target.value.length <= maxLengths.slug && undefined === prompt) {
            setForm({ ...form, slug: slugify(e.target.value.toLowerCase(), {
                strict: true, lower: true, trim: true,
            }) });
            setAdornmentText({
                ...setAdornmentText,
                slug: `${e.target.value.length} / ${maxLengths.slug}`,
            });
        } else {
            return;
        }

        if (e.target.value.length > 3) {
            ApiDataProvider.getList("prompts", {
                ...DefaultListParams,
                filter: { slug: e.target.value },
            })
                .then((resp) => {
                    if (resp.prompts.length > 0) {
                        setFormErrors({ ...formErrors, slug: "This name is already taken" });
                    } else {
                        setFormErrors({ ...formErrors, slug: "" });
                    }
                })
                .catch(() => Promise.resolve());
        }
    };

    const onChangeDescription = (e) => {
        if (e.target.value.length <= maxLengths.description) {
            setForm({ ...form, description: e.target.value });
            setAdornmentText({
                ...setAdornmentText,
                description: `${e.target.value.length} / ${maxLengths.description}`,
            });
        }

        // Change colours
        if (e.target.value.length >= maxLengths.description - alertOffset) {
            setAdornmentStyles({ ...adornmentStyles, description: { color: "error.main" } });
        } else {
            setAdornmentStyles({ ...adornmentStyles, description: { color: "text.primary" } });
        }

        checkErrors();
    };

    const onChangePromptText = (e) => {
        if (e.target.value.length <= maxLengths.prompt_text) {
            setForm({ ...form, prompt_text: e.target.value });
            setAdornmentText({
                ...setAdornmentText,
                prompt_text: `${e.target.value.length} / ${maxLengths.description}`,
            });
        }

        // Change colours
        if (e.target.value.length >= maxLengths.prompt_text - alertOffset) {
            setAdornmentStyles({ ...adornmentStyles, prompt_text: { color: "error.main" } });
        } else {
            setAdornmentStyles({ ...adornmentStyles, prompt_text: { color: "text.primary" } });
        }

        checkErrors();
    };

    const checkErrors = () => {
        let hasError = false;
        const errorMessages = { ...stateDict };
        if (form.slug.length <= 3) {
            hasError = true;
            errorMessages.slug = "Name is too short, must be 4+ characters";
        }
        if (form.description.length <= 5) {
            hasError = true;
            errorMessages.description = "Please provide a meaningful description";
        }

        if (form.prompt_text.length <= 5) {
            hasError = true;
            errorMessages.prompt_text = "Please provide a meaningful text prompt";
        }

        if (hasError) {
            setFormErrors(errorMessages);
        } else {
            // Clear the error state
            setFormErrors({ ...stateDict });
        }
        return hasError;
    };

    const doSubmit = () => {
        if (checkErrors()) {
            return;
        }

        if (!isFormSubmitted) {
            setIsFormSubmitted(true);
            if (undefined === prompt) {
                ApiDataProvider.create("prompts", {
                    data: form,
                })
                    .then((resp) => {
                        navigate(`/prompts/${resp.data.slug}`);
                    })
                    .catch((err) => {
                        setIsFormSubmitted(false);
                        console.log("err =", err);
                    });
            } else {
                ApiDataProvider.update("prompts", {
                    id: prompt.id,
                    data: form,
                })
                    .then((resp) => {
                        navigate(`/prompts/${resp.data.slug}`);
                    })
                    .catch((err) => {
                        setIsFormSubmitted(false);
                        console.log("err =", err);
                    });
            }
        }
    };

    let submitButtonDisabled = false;
    for (const k in formErrors) {
        if (formErrors[k].length > 0) {
            submitButtonDisabled = true;
        }
    }

    return (
        <>
            <Grid2 xs={12} onKeyDown={handleKeyDown}>
                <Form>
                    <Grid2 xs={12} lgOffset={3} lg={6} sx={{ mt: 1, mb: 3 }}>
                        <ConstrainedInput
                            id="slug"
                            label="Name"
                            value={form.slug}
                            disabled={undefined !== prompt ? true : false}
                            onChange={onChangeSlug}
                            maxLength={maxLengths.slug}
                            adornmentText={adornmentText.slug}
                            adornmentStyles={adornmentStyles.slug}
                            error={formErrors.slug.length > 0}
                            helperText={
                                formErrors.slug.length > 0 ? (
                                    <Box component="span" sx={{ color: "error.main" }}>
                                        {formErrors.slug}
                                    </Box>
                                ) : (
                                    "A memorable, one-word name. This can be used as an irc bot command. Must be lowercase"
                                )
                            }
                        />
                    </Grid2>
                    <Grid2 xs={12} lgOffset={3} lg={6} sx={{ mt: 1, mb: 3 }}>
                        <ConstrainedInput
                            id="description"
                            label="Human description"
                            value={form.description}
                            onChange={onChangeDescription}
                            maxLength={maxLengths.description}
                            multiline
                            rows={2}
                            adornmentText={adornmentText.description}
                            adornmentStyles={adornmentStyles.description}
                            error={formErrors.description.length > 0}
                            helperText={
                                formErrors.description.length > 0 ? (
                                    <Box component="span" sx={{ color: "error.main" }}>
                                        {formErrors.description}
                                    </Box>
                                ) : (
                                    "Provide a description for humans about what you are trying to achieve with this prompt."
                                )
                            }
                        />
                    </Grid2>

                    <Grid2 xs={12} lgOffset={3} lg={6} sx={{ mt: 1, mb: 3 }}>
                        <ConstrainedInput
                            id="slug"
                            label="Prompt text (for bots)"
                            value={form.prompt_text}
                            onChange={onChangePromptText}
                            maxLength={maxLengths.prompt_text}
                            multiline
                            rows={10}
                            adornmentText={adornmentText.prompt_text}
                            adornmentStyles={adornmentStyles.prompt_text}
                            error={formErrors.prompt_text.length > 0}
                            helperText={
                                formErrors.prompt_text.length > 0 ? (
                                    <Box component="span" sx={{ color: "error.main" }}>
                                        {formErrors.prompt_text}
                                    </Box>
                                ) : (
                                    "Provide a prompt for ChatGPT or a similar conversational bot."
                                )
                            }
                        />
                    </Grid2>
                    <Grid2 container xs={12} sx={{ mt: 1, mb: 3 }} justifyContent="end">
                        <Grid2>
                            <Button variant="text" sx={{ mr: 4 }} href="/prompts">
                                <ChevronLeft /> Cancel
                            </Button>
                            <Button
                                variant="contained"
                                disabled={submitButtonDisabled}
                                onClick={doSubmit}
                            >
                                {prompt ? (
                                    <>
                                        <Check /> Save
                                    </>
                                ) : (
                                    <>
                                        <Add /> Create
                                    </>
                                )}
                            </Button>
                        </Grid2>
                    </Grid2>
                </Form>
            </Grid2>
        </>
    );
};
