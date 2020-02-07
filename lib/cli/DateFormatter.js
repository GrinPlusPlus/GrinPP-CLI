function format(date) {
    var seconds = Math.floor((new Date() - date) / 1000);
    var intervalType;

    var interval = Math.floor(seconds / 86400);
    if (interval >= 1) {
        return date.toLocaleDateString();
    } else {
        interval = Math.floor(seconds / 3600);
        if (interval >= 1) {
            intervalType = "hour";
        } else {
            interval = Math.floor(seconds / 60);
            if (interval >= 1) {
                intervalType = "minute";
            } else {
                interval = seconds;
                intervalType = "second";
            }
        }
    }

    if (interval > 1 || interval === 0) {
        intervalType += 's';
    }

    return interval + ' ' + intervalType + ' ago';
}

module.exports = { format };