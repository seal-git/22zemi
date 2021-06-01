(function ($) {
    "use strict";

    //Generate Random Data from Sample Databaseボタンの発火
    $('.db-sample-random-generate').click(function () {
        $('.result-area').html('<font color="red">loading...</font>');
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            url: '/db_sample_random_generate',
        }).done(function (data) {
            console.log(typeof (data))
            var result = ''
            data["keys"].forEach(function (key) {
                result += key + ': ' + data["content"][key] + '<br>';
            });
            result = '<p>' + result + '</p>';
            $('.result-area').html(result);
        }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
            console.log('fail');
            $('.result-area').html('<font color="red">error!</font>');
        });

    })

})(jQuery);

