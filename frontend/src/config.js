import runtimeEnv from "@mars/heroku-js-runtime-env";

const env = runtimeEnv();
const config = {
    apiBasePath: env.REACT_APP_API_BASE_PATH || "https://botprompts.lowtech.io",
};

export default config;
