const WalletAPI = require('../../api/WalletAPI');
const Wallet = require('../Wallet');

class RestoreWallet {
    static add_command(program) {
        program.command('restore <username> <password> <seed_words...>')
            .description('Restore wallet from seed')
            .action(this.run);
    }

    static async run(username, password, seed_words) {
        const headers = {
            username: username,
            password: password
        };

        const body = {
            wallet_seed: seed_words.join(' ')
        };

        const response = await WalletAPI.POST('restore_wallet', headers, body);
        if (response != null && response.status_code == 200) {
            console.log('Wallet successfully restored!\n');
            Wallet.set_user(response.body);
        } else {
            console.error("Failed to restore wallet!\n");
            console.error(`Status: ${response.status_code}`);
            console.error(`Error: ${response.body}`);
        }
    }
}

module.exports = RestoreWallet;