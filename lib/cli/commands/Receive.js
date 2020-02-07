const fs = require('fs');
const WalletAPI = require('../../api/WalletAPI');

var help = false;
var command = null;
class Receive {
    static add_command(program) {
        command = program.command('receive <file>')
            .description('Receive slate file')
            .option('-m, --message <message>', 'Message')
            .action(this.run)
            .allowUnknownOption(true);
        command._exit = () => {};
        command.on('--help', () => { help = true; })
    }

    static async run(file, command_obj) {
        if (help) {
            help = false;
            return;
        }

        const slate = fs.readFileSync(file, 'utf-8');

        const params = {
            session_token: global.session_token,
            slate: slate,
            file: file + '.response'
        };

        if (command_obj.message != null && command_obj.message.length > 0) {
            params.message = command_obj.message;
        }

        const response = await WalletAPI.OwnerRPC('receive', params);
        if (response != null && response.result != null) {
            console.log('Received successfully');
            console.log(JSON.stringify(response.result.slate));
        } else {
            console.error("Failed to receive!\n");
            console.error(JSON.stringify(response));
        }
    }
}

module.exports = Receive;