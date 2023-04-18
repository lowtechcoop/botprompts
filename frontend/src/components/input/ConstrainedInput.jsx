import {
    Box,
    FormControl,
    FormHelperText,
    InputAdornment,
    InputLabel,
    OutlinedInput,
    useMediaQuery,
    useTheme,
} from "@mui/material";

const ConstrainedInput = (props) => {
    const {
        id,
        label,
        value,
        adornmentText,
        adornmentStyles,
        helperText,
        onChange,
        maxLength,
        ...rest
    } = props;

    const theme = useTheme();
    const isSmall = useMediaQuery(theme.breakpoints.down("sm"));

    return (
        <FormControl variant="outlined" fullWidth>
            <InputLabel htmlFor={id}>{label}</InputLabel>
            <OutlinedInput
                id={id}
                endAdornment={
                    !isSmall ? (
                        <InputAdornment disableTypography position="end" sx={adornmentStyles}>
                            {adornmentText}
                        </InputAdornment>
                    ) : undefined
                }
                aria-describedby={`${id}-helper-text`}
                inputProps={{
                    "aria-label": label,
                }}
                label={label}
                value={value}
                onChange={onChange}
                {...rest}
            />
            {isSmall && adornmentText ? (
                <Box component="div" sx={{ mt: 1, mb: 1 }}>
                    <FormHelperText id={`${id}-helper-text`} sx={adornmentStyles}>
                        Remaining characters: {adornmentText}
                    </FormHelperText>
                </Box>
            ) : undefined}
            <FormHelperText id={`${id}-helper-text`}>{helperText}</FormHelperText>
        </FormControl>
    );
};

export default ConstrainedInput;
