exports.GET = function(args) {
    // access VS Code API (s. https://code.visualstudio.com/Docs/extensionAPI/vscode-api)
    var vscode = require('vscode');
    this._terminalPid
    // current editor
    const editor = vscode.window.activeTextEditor;
    vscode.window.activeTerminal.processId.then((number) => this._terminalPid = number);
    args.response.data = {
        "activeTerminal": vscode.window.activeTerminal,
        "activeTerminalPid": this._terminalPid,
        "activeEditorSelection": (editor != undefined)? editor.selection : undefined, 
    }
    args.statusCode = 200;
}