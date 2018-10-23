jQuery.download = function(url, method, filedir, filename){
    jQuery('<form action="'+url+'" method="'+(method||'post')+'"></form>')
        .appendTo('body').submit().remove();
};


function a_json(url, type, data, success, error, cache) {
    if (type == null) type = 'GET';

    if (success == null) success = function (data) {
        swal(data.msg);
    };

    if (error == null) error = function (data){};

    if (cache == null) cache = true;


    $.ajax({
        type: type,
        url: url,
        data: data,
        cache: cache,
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            if (data.error){
                alert(data.error_message);
                location.reload();
            }
            else
                success(data);
        },
        error: function(data){
            error(data)
        }
    })
}