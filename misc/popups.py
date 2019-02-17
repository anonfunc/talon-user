popup_template = """
<style type="text/css">
body {
    padding: 0;
    margin: 0;
    font-size: 150%;
    min-width: 600px;
}

td {
    text-align: left;
    margin: 0;
    padding: 5px 10px;
}

h3 {
    padding: 5px 0px;
}

table {
    counter-reset: rowNumber;
}

table .count {
    counter-increment: rowNumber;
}

.count td:first-child::after {
    content: counter(rowNumber);
    min-with: 1em;
    margin-right: 0.5em;
}

.pick {
    font-weight: normal;
    font-style: italic;
}

.cancel {
    text-align: center;
}

</style>
"""


def list_template(list_name):
    return f"""
<div class="contents">
<h3>{list_name}</h3>
<table>
{{% for word in {list_name} %}}
<tr class="count"><td class="pick">🔊 pick </td><td>{{{{ word }}}}</td></tr>
{{% endfor %}}
<tr><td colspan="2" class="pick cancel">🔊 cancel</td></tr>
</table>
</div>
"""


def dict_to_html(title, data):
    return f"""
<div class="contents">
<h3>{title}</h3>
<table>
{"".join(['<tr><td class="pick">🔊 ' + k + '</td><td>' + v + '</td></tr>' for k,v in data.items()])}
<tr><td colspan="2" class="pick cancel">🔊 cancel</td></tr>
</table>
</div>
"""


def quickref_template(title, col1, col2, col3):
    return """
<style type="text/css">
body {
    padding: 0;
    margin: 0;
    font-size: 150%;
    min-width: 600px;
}
.quick-ref {
    grid-template: "a b c" auto;
}
#one {grid-area: a;}
#two {grid-area: b;}
#three {grid-area: c;}
</style>
""" + f"""
<h1>{title}</h1>
<div class="quickref">
<section id="one">{col1}</section>
<section id="two">{col2}</section>
<section id="three">{col3}</section>
</div>
"""