// import runtimeEnv from "@mars/heroku-js-runtime-env";
// const env = runtimeEnv();

// Depends on the use of env-cmd as part of yarn scripts (yarn build) in package.json to
// bake the REACT_APP_* keys in process.env variable
const config = {
    apiBasePath: process.env.REACT_APP_API_BASE_PATH || "https://botprompts.lowtech.io",
};

export default config;
