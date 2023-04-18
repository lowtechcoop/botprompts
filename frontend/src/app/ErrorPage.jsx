import { Box, Button, Divider, Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { useRouteError } from "react-router-dom";

const ErrorPageBase = (props) => {
    let backgroundImageUrlText = `url('${props.backgroundImage}')`;
    return (
        <>
            <Grid2
                container
                alignItems="center"
                sx={{
                    height: "100vh",
                    backgroundImage: backgroundImageUrlText,
                    backgroundSize: "cover",
                }}
            >
                <Grid2
                    xs={12}
                    lg={4}
                    lgOffset={4}
                    sx={{
                        ml: 2,
                        mr: 2,
                    }}
                >
                    <Typography
                        textAlign="center"
                        variant="h4"
                        sx={{
                            mb: 3,
                            pt: 2,
                            pb: 2,
                            color: "primary.text",
                            borderRadius: "8px",
                            background: "rgba(255, 255, 255, 0.85)",
                        }}
                    >
                        {props.title}
                    </Typography>
                    <Divider />
                    <Box
                        sx={{
                            color: "primary.contrastText",
                            bgcolor: "primary.main",
                            pt: 2,
                            pb: 4,
                            borderRadius: 2,
                        }}
                    >
                        {props.content}
                    </Box>
                </Grid2>
                <Box
                    component="div"
                    className="text-xs"
                    sx={{
                        pl: 1,
                        pr: 1,
                        height: 15,
                        position: "fixed",
                        bottom: 0,
                        background: "rgba(255, 255, 255, 0.8)",
                    }}
                >
                    {props.backgroundImageAttribution}
                </Box>
            </Grid2>
        </>
    );
};

const ErrorPage = () => {
    const errorPrimitive = useRouteError();

    let error = {
        status: 500,
        statusText: "Unknown error",
        message: "Unknown error",
    };

    if (typeof errorPrimitive === "object" && errorPrimitive !== null) {
        const errorKeys = Object.keys(errorPrimitive);

        errorKeys.forEach((k) => {
            if (k in error) {
                error[k] = errorPrimitive[k];
            }
        });
    }

    let text = (
        <>
            <Grid2
                sx={{
                    mt: 1,
                    p: 2,
                }}
            >
                <Typography variant="body1">
                    Looks like we experienced quantum tunnel decoherence. Normality is being
                    restored...
                </Typography>
                <Typography variant="body1" mt={2}>
                    There may have been something here at some point but it's gone now.
                </Typography>
                <Box mt={4} mb={3} display="flex" justifyContent="center" alignItems="center">
                    <Button
                        variant="contained"
                        href="/"
                        sx={{
                            bgcolor: "primary.light",
                        }}
                    >
                        Start Over
                    </Button>
                </Box>
                <Divider
                    sx={{
                        borderColor: "primary.light",
                    }}
                />
                <Box component="div" className="text-muted text-xs" sx={{ mt: 2 }}>
                    {error.status} {error.statusText || error.message}
                </Box>
            </Grid2>
        </>
    );

    return (
        <ErrorPageBase
            content={text}
            title="Whoops, there was an error"
            backgroundImage="/assets/error_background.jpg"
            backgroundImageAttribution="Photo by Bartosz Kwitkowski on Unsplash"
        />
    );
};

export default ErrorPage;
