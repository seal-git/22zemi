(function ($) {
    "use strict";

    //Generate Random Sentenceボタンの発火
    $('.random-generate').click(function(){
        $('.result-area').html('<font color="red">loading...</font>');
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            url: '/random',
        }).done(function(data){
            console.log(data["result"]);
            var result = '<p>'+data["result"]+'</p>';
            $('.result-area').html(result);
        }).fail(function(XMLHttpRequest, textStatus, errorThrown){
            console.log('fail');
        });

    })

})(jQuery);

