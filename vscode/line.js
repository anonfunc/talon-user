exports.GET = function(args) {
    // access VS Code API (s. https://code.visualstudio.com/Docs/extensionAPI/vscode-api)
    var vscode = require('vscode');
    // current editor
    const editor = vscode.window.activeTextEditor;
    args.response.data = {
        "selection": editor.selection,
        "path": args.path,
    }
    args.statusCode = 200;
}

exports.POST = async function(args) {
    var vscode = require('vscode');
    // current editor
    const editor = vscode.window.activeTextEditor;
    var body = await args.getJSON();
    p1l = body["start"]["line"];
    p1c = body["start"]["character"];
    p2l = body["end"]["line"];
    p2c = body["end"]["character"];
    const start = new vscode.Position(p1l, p1c);
    const end = new vscode.Position(p2l, p2c);
    editor.selection = new vscode.Selection(start, end);
    editor.revealRange(new vscode.Range(start, end), 1);
}