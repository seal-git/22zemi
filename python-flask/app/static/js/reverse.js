(function ($) {
    "use strict";

    //submitボタンを押したらajax通信で内容をPOSTする
    $('.reverse-sentence').submit(function(event){
        event.preventDefault();
        $('.result-area').html('<font color="red">loading...</font>');
        var data = $('.contact100-form [name=name]').val();
        data = JSON.stringify(data);
        // console.log(data)
        $.ajax({
            type: 'POST',
            data: data,
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            url: '/reverse',
        }).done(function(data){
            console.log(data["result"]);
            var result = '<p>'+data["result"]+'</p>';
            $('.result-area').html(result);
            $('.reverse-sentence')[0].reset();

        }).fail(function(XMLHttpRequest, textStatus, errorThrown){
            console.log('fail');
        });
    });

    //Submit Random Sentenceボタンの発火
    $('.reverse-submit-random').on('click', function(){
        $('.result-area').html('<font color="red">loading...</font>');
        $.ajax({
            type: 'POST',
            url: '/reverse_random',
        }).done(function(data){
            console.log(data["result"]);
            var result = '<p>'+data["result"]+'</p>';
            $('.result-area').html(result);
        }).fail(function(XMLHttpRequest, textStatus, errorThrown){
            console.log('fail');
        });

    })


})(jQuery);

