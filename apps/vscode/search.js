exports.POST = async function(args) {
    var vscode = require('vscode');
            
    // current editor
    const editor = vscode.window.activeTextEditor;
    const position = editor.selection.active;
    var body = await args.getJSON();
    direction = body["direction"];
    pattern = body["string"];
    const start = new vscode.Position(position.line, position.character);
    const startOffset = editor.document.offsetAt(start);
    const text = editor.document.getText();
    var textToSearch;
    var index;
    var newIndex;
    if (direction == "forward") {
        textToSearch = text.substring(startOffset+1, text.length).toLowerCase();
        index = textToSearch.indexOf(pattern.toLowerCase());
        newIndex = startOffset + index + 1;
    } else {
        textToSearch = text.substring(0, startOffset-1).toLowerCase();
        index = textToSearch.lastIndexOf(pattern.toLowerCase());
        newIndex = index;
    }
    // vscode.window.showInformationMessage('('+ newIndex + ", " + pattern.length + ") " + pattern);
    const beginning = editor.document.positionAt(newIndex);
    const end = editor.document.positionAt(newIndex+pattern.length);
    editor.selection = new vscode.Selection(beginning, end);
    editor.revealRange(new vscode.Range(beginning, end), 1);
}