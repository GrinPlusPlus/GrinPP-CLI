const WalletAPI = require('../../api/WalletAPI');
const SendToHTTP = require('../../api/SendToHTTP');

var help = false;
var command = null;
class Send {
    static add_command(program) {
        command = program.command('send <amount>')
            .usage('-m <method> -d <destination> <amount>')
            .description('Send grins (ex. send -m tor -d 3ngg5chiucyvjxaymy46fypqbr3nfskj2lluygnz6hqys5lwxrcpqzad 2.5)')
            .requiredOption('-m, --method <method>', 'Send method (tor, http, file)')
            .requiredOption('-d, --destination <destination>', 'Destination file or address')
            .action(this.run)
            .allowUnknownOption(true);
        command._exit = () => {};
        command.on('--help', () => { help = true; })
    }

    static async run(amount, command_obj) {
        if (help) {
            help = false;
            return;
        }

        if (command_obj.destination == null) {
            console.error('destination required');
            return;
        }

        var params = {
            session_token: global.session_token,
            amount: amount * Math.pow(10, 9),
            fee_base: 1000000,
            selection_strategy: { strategy: 'SMALLEST' },
            post_tx: { method: 'STEM' }
        };

        const method = command_obj.method == null ? null : command_obj.method.toLowerCase();
        if (method == 'tor') {
            params.address = command_obj.destination;
        } else if (method == 'file') {
            params.file = command_obj.destination;
        } else if (method == 'http') {
            return await SendToHTTP.send(command_obj.destination, amount * Math.pow(10, 9));
        } else {
            console.error('method required (tor, http, file)');
            return;
        }
    
        const response = await WalletAPI.OwnerRPC('send', params);
        if (response != null && response.result != null) {
            console.log('Sent successfully');
            console.log(JSON.stringify(response.result.slate));
        } else {
            console.error("Failed to send!\n");
            console.error(JSON.stringify(response));
        }
    }
}

module.exports = Send;