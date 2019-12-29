
import { getUsefulContents } from './functions.js';
import { formatParams } from './functions.js';


$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

// function formatParams( params ){
//     return "?" + Object
//           .keys(params)
//           .map(function(key){
//             return key+"="+encodeURIComponent(params[key])
//           })
//           .join("&")
//   }

function get_callback(data){
    var error_code = "";
    var data;
    var des = "";
    var status = "";
    $.each(data, function(key, value){
        console.log(key, value)
        if( key == "error")
        {
            error_code = value;
        }
        else if( key == "data")
        {
            data = value;
        }
        else if( key == "status")
        {
            status = value;
        }
        else if( key == "des")
        {
            des = value;
        }
    });


    if( error_code == "0" )
    {
        localStorage.setItem("user_name", data['user']);
        window.location.href = "http://127.0.0.1:5000/user";

    }
    else
    {
        alert(des);
    }


    // if( data == "valid" )
    // {
    //     localStorage.setItem("TechARide","TAR");
    //     window.location.href = "http://127.0.0.1:5000/user";
    // }
    // else
    // {
    //     alert("error user name");
    // }
}
function post_callback(data){
    var error_code = "";
    var data;
    var des = "";
    var status = "";
    $.each(data, function(key, value){
        console.log(key, value)
        if( key == "error")
        {
            error_code = value;
        }
        else if( key == "data")
        {
            data = value;
        }
        else if( key == "status")
        {
            status = value;
        }
        else if( key == "des")
        {
            des = value;
        }
    });


    if( error_code == "0" )
    {
        localStorage.setItem("user_name", data['user']);
        alert("註冊成功");
        window.location.href = "http://127.0.0.1:5000/";

    }
    else
    {
        alert(des);
    }
}

$(function() {

    $('form.login').on('submit', function(e) {
        e.preventDefault();

        var formData = $(this).serializeObject();

        $('.datahere').html(formData);
        var url = "http://127.0.0.1:5000/auth" +formatParams(formData);

        getUsefulContents(url, 'GET', "", data => { get_callback(data); });
    });

    //sign up event
    $("#btn_signup").click(function(event) {

        var input_data = new Object();
        input_data['user_name'] = $('#orangeForm-name').val()
        input_data['password'] = $('#orangeForm-pass').val()
        var url = "http://127.0.0.1:5000/auth"
        getUsefulContents(url, "POST", input_data, data => { post_callback(data); });

    });

});
