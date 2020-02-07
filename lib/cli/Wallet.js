class Wallet {
    static set_user(body) {
        global.session_token = body.session_token;
        global.tor_address = body.tor_address;
        global.listener_port = body.listener_port;

        this.display_info();
    }

    static display_info() {
        console.log(`Listening on port ${global.listener_port}\n`);
        if (global.tor_address != null) {
            console.log(`${global.tor_address}`);
            console.log(`http://${global.tor_address}.grinplusplus.com`);
            console.log();
        }
    }
}

module.exports = Wallet;