const WalletAPI = require('../../api/WalletAPI');

class Exit {
    static add_command(program) {
        program.command('exit')
            .description('Exit')
            .action(this.run);
    }

    static async run() {
        if (global.session_token != null) {
            const headers = {
                session_token: global.session_token
            };

            await WalletAPI.POST('logout', headers);
        }

        process.exit(0);
    }
}

module.exports = Exit;