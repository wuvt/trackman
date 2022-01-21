// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-v3.0

function initLocalDates() {
    $('time').each(function() {
        var datestr = $(this).attr('datetime');
        var format = $(this).attr('data-format');
        var m = moment(datestr);
        if(m.isValid()) {
            $(this).text(m.format(format));
            $(this).attr('title', m.format('LLLL'));
        }
    });
}

// @license-end
