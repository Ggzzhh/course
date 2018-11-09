jQuery.download = function(url, method, filedir, filename){
    jQuery('<form action="'+url+'" method="'+(method||'post')+'"></form>')
        .appendTo('body').submit().remove();
};


function a_json(url, type, data, success, error, cache) {
    if (type == null) type = 'GET';

    if (success == null) success = function (data) {
        swal(data.msg);
    };

    if (error == null) error = function (data){
        swal(data.msg, '', 'error')
    };

    if (cache == null) cache = true;

    if (data == null) data = JSON.stringify({});

    $.ajax({
        type: type,
        url: url,
        data: data,
        cache: cache,
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            if (data.resCode === 'err')
                error(data);
            else
                success(data);
        },
        error: function(data){
            error(data)
        }
    })
}

function getQueryVariable(key){
    let reg = new RegExp("(^|&)"+ key +"=([^&]*)(&|$)");
    let re = window.location.search.substr(1).match(reg);
    if (re != null)
        return decodeURI(re[2]);
    else
        return null;
}