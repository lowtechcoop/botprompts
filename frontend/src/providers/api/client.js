import axios from "axios";
import config from "../../config";

class ApiClientBase {

     API_URL;

     CLIENT;

     constructor(config) {
        this.API_URL = `${config.apiBasePath}/api/v1`;
        this.CLIENT = axios.create({ baseURL: this.API_URL });
     }

    getApiUrl() {
        return this.API_URL;
    }

    getClient() {
        return this.CLIENT;
    }
}

const ApiClient = new ApiClientBase(config);

export default ApiClient;
