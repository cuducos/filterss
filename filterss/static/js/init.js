$(document).ready(function(){


    $('#title_inc').tagsInput({'defaultText': '…'});
    $('#title_exc').tagsInput({'defaultText': '…'});
    $('#link_inc').tagsInput({'defaultText': '…'});
    $('#link_exc').tagsInput({'defaultText': '…'});

    set_submit(false)
    $('#rss_url').blur(check_url)
    check_url()

})

set_feedback = function (value) {
    feedback = $('#url_feedback')
    fieldset = $('#rss_url_fieldset')
    if ( value ) {
        fieldset.addClass('has-success').removeClass('has-error')
        feedback.show().addClass('glyphicon-ok').removeClass('glyphicon-remove')
        set_submit(true)
    } else {
        fieldset.addClass('has-error').removeClass('has-success')
        feedback.show().addClass('glyphicon-remove').removeClass('glyphicon-ok')
        set_submit(false)

    }

}

set_submit = function (value) {
    btn = $('#submit_btn')
    if ( value ) {
        btn.removeAttr('disabled')
    } else {
        btn.attr('disabled', 'disabled')
    }
}

check_url = function () {
    url = $('#rss_url').val()
    $.get( "/check_url?&url=" + escape(url), function( data ) {
        if (data == 'False') {
            set_feedback(false)
        } else {
            set_feedback(true)
            if (data != 'True') {
                $('#rss_url').val(data)
            }
        }
    });
}