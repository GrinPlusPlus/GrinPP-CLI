const axios = require('axios');

class WalletAPI {
    static async OwnerRPC(method, params) {
        const url = 'http://localhost:3421/v2';
        
        return await this.RPC(url, method, params);
    }

    static async RPC(url, method, params) {
        try {
            const body = {
                id: '0',
                jsonrpc: '2.0',
                method: method,
                params: params
            };
            const response = await axios.post(url, body);
            return {
                error: response.data.error || null,
                result: response.data.result || null
            };
        } catch (e) {
            return {
                status_code: e.response.status,
                body: e.response.data
            };
        }
    }

    static async POST(action, headers, body = {}) {
        const url = 'http://localhost:3420/v1/wallet/owner/' + action;
        
        try {
            const response = await axios.post(url, body, { headers: headers});
            return {
                status_code: response.status,
                body: response.data
            };
        } catch (e) {
            return {
                status_code: e.response.status,
                body: e.response.data
            };
        }
    }

    static async GET(action, headers, params = {}) {
        const url = 'http://localhost:3420/v1/wallet/owner/' + action;

        try {
            const response = await axios.get(url, { params: params, headers: headers});
            return {
                status_code: response.status,
                body: response.data
            };
        } catch (e) {
            return {
                status_code: e.response.status,
                body: e.response.data
            };
        }
    }
}

module.exports = WalletAPI;