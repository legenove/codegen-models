/*
 接口定义
 */
var http = require('../../http/base.js');

var app = getApp();

var {{name}} = function () {

    {%- for method, ins in methods.items() %}
    /*
        @params obj 'data params'
            {%- if ins['headers'] -%}
            {% for _h in ins['headers'] -%}
            {{_h.get('name')}}   '{{_h.get('type')}}' {% if 'description' in _h %}{{_h.get('description')}}{% endif %}
            {%- endfor %}
            {%- endif %}
            {% if ins['path'] -%}
            {% for _h in ins['path'] -%}
            {{_h.get('name')}}   '{{_h.get('type')}}' {% if 'description' in _h %}{{_h.get('description')}}{% endif %}
            {% endfor -%}
            {%- endif -%}
            {% if ins['params'] -%}
            {% for _h in ins['params'] -%}
            {{_h.get('name')}}   '{{_h.get('type')}}' {% if 'description' in _h %}{{_h.get('description')}}{% endif %}
            {% endfor -%}
            {%- endif %}
        @success
            {% for _h,_v in ins['response'].items() -%}
            status {{_h}}    type:{{_v['type']}}
            {%- if _v['type'] == 'array'%}
            {% for _h in _v['items'] -%}
            {{_h.get('name')}}   '{{_h.get('type')}}' {% if 'description' in _h %}{{_h.get('description')}}{% endif %}
            {% endfor -%}
            {%- else %}
            {%- if 'properties' in _v %}
            {% for _h in _v['properties'] -%}
            {{_h.get('name')}}   '{{_h.get('type')}}' {% if 'description' in _h %}{{_h.get('description')}}{% endif %}
            {% endfor -%}
            {% endif %}
            {%- endif -%}
            {% endfor %}
    */
    this.{{method.lower()}} = function (that, obj){
        http.request({
            baseUrl: "{{ base_path }}",
            url: {{ url }},
            method: "{{method.upper()}}",
            {%- if ins['headers'] %}
            headers: {
                {% for _h in ins['headers'] -%}
                {{_h.get('name')}}: obj.{{_h.get('name')}} {%- if not loop.last %},{% endif %}
                {% endfor -%}
            },
            {%- endif %}
            {%- if ins['params'] %}
            data: {
                {% for _h in ins['params'] -%}
                {{_h.get('name')}}: obj.{{_h.get('name')}} {%- if 'default' in _h and _h.get('type') in ['integer', 'string'] %} || {% if _h.get('type') == 'integer' -%}
                {{_h.get('default')}}
                {%- else -%}
                "{{_h.get('default')}}"
                {%- endif %}{% endif %}{%- if not loop.last %},{% endif %}
                {% endfor -%}
            },
            {%- endif %}
            success: function (res) {
                typeof obj.success === 'function' && obj.success(res);
            },
            fail: function (res) {
                typeof obj.fail === 'function' && obj.fail(res);
            },
            complete: function (res) {
                typeof obj.complete === 'function' && obj.complete(res);
            }
        })
    };
    {% endfor %}

};

module.exports = {
    {{name}}: new {{name}}
};