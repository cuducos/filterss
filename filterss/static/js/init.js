$(document).ready(function(){

    $('#t_inc').tagsInput({'defaultText': '…'});
    $('#t_exc').tagsInput({'defaultText': '…'});
    $('#l_inc').tagsInput({'defaultText': '…'});
    $('#l_exc').tagsInput({'defaultText': '…'});

    set_submit(false);
    $('#rss_url').blur(check_url);
    if ($('#rss_url').val() != '') {
        check_url();
    }

})

set_feedback = function (value) {
    feedback = $('#url_feedback');
    fieldset = $('#rss_url_fieldset');
    if ( value ) {
        fieldset.addClass('has-success').removeClass('has-error');
        feedback.show().addClass('glyphicon-ok').removeClass('glyphicon-remove');
        set_submit(true);
    } else {
        fieldset.addClass('has-error').removeClass('has-success');
        feedback.show().addClass('glyphicon-remove').removeClass('glyphicon-ok');
        set_submit(false);
    }
}

set_submit = function (value) {
    btn = $('#submit_btn');
    if ( value ) {
        btn.removeAttr('disabled');
    } else {
        btn.attr('disabled', 'disabled');
    }
}

check_url = function () {

    // set basic vars
    var obj = $('#rss_url');
    var url = obj.val();
    var regexp = /(feed|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
    var valid = regexp.test(url);

    // if fails, try to add protocol
    if (!valid && no_protocol) {
        new_url = 'http://' + url;
        valid = regexp.test(new_url);
    }

    // test url
    if (valid) {
        set_feedback(true);
        obj.val(replace_protocol(url));
    } else {
        set_feedback(false);
    }
}

replace_protocol = function (url) {
    if (url.indexOf('feed://') == 0) {
        return url.replace('feed://', 'http://');
    }
    if (url.indexOf('https://') == 0) {
        return url.replace('https://', 'http://');
    }
    return url;
}

no_protocol = function (url) {
    var regexp = /(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
    return regexp.test(url);
}
