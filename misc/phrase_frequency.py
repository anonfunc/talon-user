from talon import ui, webview
from talon.engine import engine
from talon.voice import Context

from collections import defaultdict

template = """
<style type="text/css">
body {
    width: 400px;
    padding: 0;
    margin: 0;
}
.contents, table, h3 {
    width: 100%;
}
table {
    table-layout: fixed;
}
td {
    overflow-wrap: normal;
    word-wrap: normal;
    text-align: left;
    margin: 0;
    padding: 0;
    padding-left: 5px;
    padding-right: 5px;
}
.text {
    font-weight: normal;
    font-style: italic;
}
#title {
    padding-right: 5px; /* this is broken */
    min-width: 100px;
}
</style>

<h3 id="title">Counts</h3>
<table>
{% for phrase, text in phrases %}
<tr><td class="phrase">{{ phrase }}</td><td class="text">{{ text }}</td></tr>
{% endfor %}
<tr><td><i>{{ hypothesis }}</i></td></tr>
</ul>
"""

webview = webview.Webview()
webview.render(template, phrases=[("command", "")])
webview.move(0, ui.main_screen().height)

webview_shown = False


def toggle_webview(m):
    global webview_shown
    if webview_shown:
        webview.hide()
    else:
        webview.show()
    webview_shown = not webview_shown


class History:
    def __init__(self):
        self.history = defaultdict(int)
        engine.register("post:phrase", self.on_phrase_post)

    def parse_phrase(self, phrase):
        return " ".join(word.split("\\")[0] for word in phrase)

    def on_phrase_post(self, j):
        phrase = self.parse_phrase(j.get("phrase", []))
        if phrase in ("toggle frequency", "pa"):
            return
        cmd = j["cmd"]
        if cmd == "p.end" and phrase:
            self.history[phrase] += 1
        by_count = sorted(self.history.items(), reverse=True, key=lambda v: v[1])[:50]
        # print(by_count)
        webview.render(template, phrases=by_count)


history = History()
ctx = Context("phrase_frequency")
ctx.keymap({"toggle frequency": toggle_webview})
# webview.show()
