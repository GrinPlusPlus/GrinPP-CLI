const WalletAPI = require('../../api/WalletAPI');
const Wallet = require('../Wallet');

class CreateWallet {
    static add_command(program) {
        program.command('create <username> <password>')
            .description('Create new wallet')
            .action(this.run);
    }

    static async run(username, password) {
        const headers = {
            username: username,
            password: password
        };

        const response = await WalletAPI.POST('create_wallet', headers);
        if (response != null && response.status_code == 200) {
            console.log('Wallet successfully created!\n');
            console.log(response.body.wallet_seed);
            console.log();
            
            Wallet.set_user(response.body);
        } else {
            console.error("Failed to create wallet!\n");
            console.error(`Status: ${response.status_code}`);
            console.error(`Error: ${response.body}`);
        }
    }
}

module.exports = CreateWallet;