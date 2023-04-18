class AppHttpError extends Error {
    status = 0;

    constructor(params) {
        super(params.statusText);
        this.status = params.status
        this.statusText = params.statusText
    }
}

export default AppHttpError;
