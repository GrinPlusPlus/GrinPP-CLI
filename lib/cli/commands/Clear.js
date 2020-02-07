const WalletAPI = require('../../api/WalletAPI');
const Tables = require('../Tables');
const Wallet = require('../Wallet');

class Summary {
    static add_command(program) {
        program.command('clear')
            .description('Clears screen')
            .action(this.run);
    }
    
    static async run(command_obj) {
        console.clear();
    }
}

module.exports = Summary;