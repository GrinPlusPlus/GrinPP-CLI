const WalletAPI = require('../../api/WalletAPI');
const Wallet = require('../Wallet');

class OpenWallet {
    static add_command(program) {
        program.command('open <username> <password>')
            .description('Open wallet')
            .action(this.run);
    }

    static async run(username, password) {
        process.stdout.write('Logging in')
        const interval = setInterval(() => {  process.stdout.write('.'); }, 2500);

        const headers = {
            username: username,
            password: password
        };

        const response = await WalletAPI.POST('login', headers);
        if (response != null && response.status_code == 200) {
            clearInterval(interval);
            console.clear();
            
            Wallet.set_user(response.body);
        } else {
            clearInterval(interval);
            console.clear();

            console.error("Failed to open wallet!\n");
            console.error(`Status: ${response.status_code}`);
            console.error(`Error: ${response.body}`);
        }
    }
}

module.exports = OpenWallet;