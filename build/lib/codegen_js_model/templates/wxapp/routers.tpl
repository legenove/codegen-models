//RoutersApis -- {{base_path}}{{tag_name}}Model.js

{% include '_do_not_change.tpl' %}

{% for view in views -%}
var {{view.name}}Model = require('./{{base_path}}/{{view.endpoint}}.js');
{% endfor %}
module.exports = {
    {% for view in views -%}
    {{view.name}}: {{view.name}}Model.{{view.name}} {% if not loop.last %},{% endif %}
    {% endfor %}};