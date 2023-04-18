import ApiClient from "./client";
import queryString from "query-string";

export const ApiDataProvider = {
    getList(resource, params) {
        const { page, perPage } = params.pagination;
        const { field, order } = params.sort;
        const query = {
            sort_field: field,
            sort_order: order,
            range_start: (page - 1) * perPage,
            range_end: page * perPage - 1,
            filter_input: JSON.stringify(params.filter),
            history: params.history || false,
        };
        const url = `${ApiClient.getApiUrl()}/${resource}?${queryString.stringify(query)}`;

        return ApiClient.getClient()
            .get(url)
            .then((resp) => Promise.resolve(resp.data))
            .catch((err) => {
                console.log(err);
                Promise.reject(err);
            });
    },

    /**
     * Specific to prompts, gets a flat list of current prompt + revision
     * @returns
     */
    getCurrentPromptsList() {
        const url = `${ApiClient.getApiUrl()}/prompts/current`;

        return ApiClient.getClient()
            .get(url)
            .then((resp) => Promise.resolve(resp.data))
            .catch((err) => {
                console.log(err);
                Promise.reject(err);
            });
    },

    getOne(resource, params) {
        const query = {
            ids: JSON.stringify([params.id]),
        };
        const url = `${ApiClient.getApiUrl()}/${resource}?${queryString.stringify(query)}`;
        return ApiClient.getClient()
            .get(url)
            .then((resp) => {
                console.log("getOne-->resp", {
                    data: resp.data.data,
                });

                return Promise.resolve({ data: resp.data.data[0] });
            })
            .catch((err) => {
                console.log("getOne-->err", err);
                return Promise.resolve({ data: err });
            });
    },

    create(resource, params) {
        const url = `${ApiClient.getApiUrl()}/${resource}`;

        return ApiClient.getClient()
            .post(url, { ...params.data })
            .then((resp) => {
                return Promise.resolve({ data: resp.data });
            })
            .catch((err) => {
                const error_payload = { errors: {} };
                err.response.data.detail.forEach((e) => {
                    error_payload.errors[e.loc] = `${e.message} error_type:${e.type}`;
                });
                return Promise.reject({
                    statusText: err.response.statusText,
                    status: err.response.status,
                    payload: error_payload,
                });
            });
    },

    update(resource, params) {
        const url = `${ApiClient.getApiUrl()}/${resource}`;
        const payload = {
            ids: [params.id],
            data: params.data,
        };
        return ApiClient.getClient()
            .put(url, payload)
            .then((resp) => {
                return Promise.resolve({ data: resp.data });
            })
            .catch((err) => {
                const error_payload = { errors: {} };
                err.response.data.detail.forEach((e) => {
                    error_payload.errors[e.loc] = `${e.message} error_type:${e.type}`;
                });
                return Promise.reject({
                    statusText: err.response.statusText,
                    status: err.response.status,
                    payload: error_payload,
                });
            });
    },
};

export const DefaultListParams = {
    pagination: { page: 0, perPage: 100 },
    filter: {},
    sort: { field: "id", order: "ASC" },
};
