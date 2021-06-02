
(function ($) {
    "use strict";
    //sentenceを読み込む関数
    function get_sentence(){
        $('.sentence-area').html('<font color="red">loading...</font>');
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            url: '/db_sample_random_generate',
        }).done(function(data){
            var result = data["content"]["sentence"]
            result = '<p>' + result + '</p>';
            $('.sentence-area').html(result);
        }).fail(function(XMLHttpRequest, textStatus, errorThrown){
            console.log('fail');
        });
    }

    //ページ読み込み時にsentenceを取得
    $(document).ready(function(){
        get_sentence();
    });
    //reloadボタンの発火
    $('.btn-reload').click(function(){
        get_sentence()
    });

    //yesボタンの発火
    $('.btn-yes').click(function(){
        $('.result-area').html('<font color="red">loading...</font>');
        $.ajax({
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            url: '/get_feedback_yes_no',
        }).done(function(data){

            get_sentence();
        }).fail(function(XMLHttpRequest, textStatus, errorThrown){
            console.log('fail');
        });

    })

})(jQuery);

