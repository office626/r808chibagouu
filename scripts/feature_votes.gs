/**
 * 運用スプレッドシート用の投票 API。
 * シートに紐づけて貼るか、スタンドアロンでも動く（下の ID で開く）。
 *
 * 公開手順（ブラウザ）:
 * 1. シートを開く → 拡張機能 → Apps Script
 * 2. このファイルの中身を Code.gs に貼る → 保存
 * 3. デプロイ → 新しいデプロイ → 種類: ウェブアプリ
 * 4. 次のユーザーとして実行: 自分
 * 5. アクセスできるユーザー: 全員
 * 6. デプロイ → 表示された URL（末尾 /exec）を vote-config.json の endpoint へ
 */
var SPREADSHEET_ID = "1_dHZHMLvTx6iTCzwvbw6U9cTHjTIH_6RlEob81Ng7KM";
var SHEET_NAME = "feature_votes";

function ss_() {
  var active = SpreadsheetApp.getActive();
  if (active && String(active.getId()) === SPREADSHEET_ID) return active;
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function sheet_() {
  var ss = ss_();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(["idea_id", "voter", "at"]);
  }
  if (sh.getLastRow() === 0) sh.appendRow(["idea_id", "voter", "at"]);
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function counts_(sh) {
  var rows = sh.getDataRange().getValues();
  var counts = {};
  for (var i = 1; i < rows.length; i++) {
    var id = String(rows[i][0] || "");
    if (!id) continue;
    counts[id] = (counts[id] || 0) + 1;
  }
  return counts;
}

function findRow_(sh, idea, voter) {
  var rows = sh.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === idea && String(rows[i][1]) === voter) return i + 1;
  }
  return 0;
}

function doGet(e) {
  e = e || { parameter: {} };
  var p = e.parameter || {};
  var sh = sheet_();
  var action = p.action || "list";
  var idea = String(p.idea || "");
  var voter = String(p.voter || "").slice(0, 80);

  if (action === "vote" && idea && voter) {
    if (!findRow_(sh, idea, voter)) {
      sh.appendRow([idea, voter, new Date().toISOString()]);
    }
  }
  if (action === "unvote" && idea && voter) {
    var row = findRow_(sh, idea, voter);
    if (row) sh.deleteRow(row);
  }
  return json_({ counts: counts_(sh) });
}

/** エディタで実行して、シート feature_votes が作られるか確認する。 */
function test_createSheet() {
  var sh = sheet_();
  Logger.log("ok " + sh.getName() + " rows=" + sh.getLastRow());
}
