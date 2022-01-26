// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-v3.0

function createLink(url, text) {
    var link = document.createElement('a');
    link.href = url;
    $(link).text(text);
    return link;
}

function initNowPlaying() {
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
                var track = msg['tracklog']['track'];

                $('#now_playing_track').html(createLink(
                    "/playlists/track/" + track['id'],
                    track['title']));
                $('#now_playing_artist').text(track['artist']);
                $('#now_playing_album').text(track['album']);

                if(msg['tracklog']['dj_visible']) {
                    $('#now_playing_dj').html(createLink(
                        "/playlists/dj/" + msg['tracklog']['dj_id'],
                        msg['tracklog']['dj']));
                } else {
                    $('#now_playing_dj').text(msg['tracklog']['dj']);
                }

                break;
        }
    };
}

initNowPlaying();

// @license-end
