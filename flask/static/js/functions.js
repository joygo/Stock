
// function get_url(url, method, async, params) {
//     var xhttp = new XMLHttpRequest();
//     xhttp.open(method, url, async);
//     xhttp.send();
//     // waitUI();
//     var data = xhttp.responseText;
//     return data;
// }

function getJSON(url, method, params, callback) {
    let xhr = new XMLHttpRequest();
    xhr.onload = function () {
        // alert(this.responseText);
        callback(this.responseText)
    };
    xhr.open(method, url, true)
    if(params)
        {
            console.log(params);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(params));

        }
    else
    {
        xhr.send();

    }
  }

export function formatParams( params ){
return "?" + Object
        .keys(params)
        .map(function(key){
        return key+"="+encodeURIComponent(params[key])
        })
        .join("&")
}

export function getUsefulContents(url, method, params, callback) {
    getJSON(url, method, params, data => callback(JSON.parse(data)));
}