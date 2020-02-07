const fs = require('fs');
const WalletAPI = require('../../api/WalletAPI');

var help = false;
var command = null;
class Receive {
    static add_command(program) {
        command = program.command('finalize <file>')
            .description('Finalize slate file')
            .action(this.run)
            .allowUnknownOption(true);
        command._exit = () => {};
        command.on('--help', () => { help = true; })
    }

    static async run(file) {
        if (help) {
            help = false;
            return;
        }

        const slate = fs.readFileSync(file, 'utf-8');

        const params = {
            session_token: global.session_token,
            slate: slate,
            file: file + '.finalized',
            post_tx: { method: 'STEM' }
        };

        const response = await WalletAPI.OwnerRPC('finalize', params);
        if (response != null && response.result != null) {
            console.log('Finalized successfully');
            console.log(JSON.stringify(response.result.slate));
        } else {
            console.error("Failed to finalize!\n");
            console.error(JSON.stringify(response));
        }
    }
}

module.exports = Receive;