const WalletAPI = require('./WalletAPI');

async function callFinalize(slate) {
    const params = {
        session_token: global.session_token,
        slate: slate,
        post_tx: { method: 'STEM' }
    };

    const response = await WalletAPI.OwnerRPC('finalize', params);
    if (response != null && response.result != null) {
        console.log('Slate finalized:');
        console.log(JSON.stringify(response.result.slate));
        return response.result.slate;
    } else {
        console.error("Failed to finalize!\n");
        console.error(JSON.stringify(response));
        return null;
    }
}

async function callReceive(httpAddress, slate) {
    const response = await WalletAPI.RPC(httpAddress + '/v2/foreign', 'receive_tx', [slate, null, '']);
    if (response.result != null && response.result.Ok != null) {
        console.log('Slate Received:');
        console.log(JSON.stringify(response.result.Ok));
        return response.result.Ok;
    } else {
        console.error('Failed while contacting receiver!');
        console.error(JSON.stringify(response));
        return null;
    }
}

async function callSend(httpAddress, amount) {
    console.log(global.session_token);
    const params = {
        session_token: global.session_token,
        amount: amount,
        fee_base: 1000000,
        selection_strategy: { strategy: 'SMALLEST' },
        post_tx: { method: 'STEM' },
        address: httpAddress
    };

    const response = await WalletAPI.OwnerRPC('send', params);
    if (response != null && response.result != null) {
        console.log('Slate created:');
        console.log(JSON.stringify(response.result.slate));
        return response.result.slate;
    } else {
        console.error("Failed to send!\n");
        console.error(JSON.stringify(response));
        return null;
    }
}

async function send(httpAddress, amount) {
    console.log("Sending to: " + httpAddress);

    const sent_slate = await callSend(httpAddress, amount);
    if (sent_slate == null) {
        return;
    }

    const received_slate = await callReceive(httpAddress, sent_slate);
    if (received_slate == null) {
        return;
    }

    const finalized_slate = await callFinalize(received_slate);
    if (finalized_slate == null) {
        return;
    }

    console.log('Transaction sent successfully!');
};

module.exports = {send}