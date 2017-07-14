// http/base.js

/**
 * 封装 wx.request
 */
function updateJson(orgin, update) {
    for (var k in update) {
        if (update[k] != null){
            orgin[k] = update[k];
        }
    }
    return orgin
}

function cleanJson(orgin){
    var target = {};
    for (var k in orgin) {
        if (orgin[k] != null){
            target[k] = orgin[k];
        }
    }
    return target
}

function request(option) {
    var api_host = 'https://zaih.com';
    var Authorization = option.Authorization || 'Basic 123';
    wx.request({
        url: api_host + option.baseUrl + option.url,
        data: cleanJson(option.data) || {},
        method: option.method && option.method.toUpperCase() || 'GET',
        header: updateJson({
            'content-type': 'application/json',
            'Authorization': Authorization
        }, option.header || {}),
        success: function (res) {
            var code = res.statusCode;
            if (/^2\d{2}$/.test(code)) {
                typeof option.success === 'function' && option.success(res);
            } else {
                typeof option.fail === 'function' && option.fail(res);
            }
        },
        fail: function (res) {
            typeof option.fail === 'function' && option.fail(res);
        },
        complete: function (res) {
            typeof option.complete === 'function' && option.complete(res);
        }
    })
}

module.exports = {
    request: request
};