
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




    /*==================================================================
    [ Validate after type ]*/
    $('.validate-input .input100').each(function(){
        $(this).on('blur', function(){
            if(validate(this) == false){
                showValidate(this);
            }
            else {
                $(this).parent().addClass('true-validate');
            }
        })    
    })
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
           $(this).parent().removeClass('true-validate');
        });
    });

     function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');

        $(thisAlert).append('<span class="btn-hide-validate">&#xf136;</span>')
        $('.btn-hide-validate').each(function(){
            $(this).on('click',function(){
               hideValidate(this);
            });
        });
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();
        $(thisAlert).removeClass('alert-validate');
        $(thisAlert).find('.btn-hide-validate').remove();
    }
    
    

})(jQuery);