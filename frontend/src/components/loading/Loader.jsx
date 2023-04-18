import { Box } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import HashLoader from "react-spinners/HashLoader";

export const Loader = (props) => {
    // https://www.davidhu.io/react-spinners/storybook/?path=/docs/hashloader--main
    return (
        <Grid2 container alignItems="center" justifyContent="center">
            <Box sx={{ mt: 10, mb: 10, p: 2 }}>
                <HashLoader
                    color={props.color || "#3663d6"}
                    size={props.size || 50}
                    loading={props.loading || true}
                    cssOverride={props.sx || {}}
                    speedMultiplier={props.speedMultiplier || 1.0}
                />
            </Box>
        </Grid2>
    );
};
