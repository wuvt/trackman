// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-v3.0

function initLast15() {
    if(typeof EventSource == 'undefined') {
        // cannot use server-sent events, boo
        return;
    }

    var source = new EventSource("/live");
    source.onmessage = function(ev) {
        msg = JSON.parse(ev.data);

        switch(msg['event']) {
            case 'track_change':
            case 'track_delete':
            case 'track_edit':
                location.reload();
                break;
        }
    };
}

initLast15();

// @license-end
