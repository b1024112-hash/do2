// 対象のAPI URL
const targetApiUrl = 'https://api.buoy.jp/sakura/table.php?lfourId=1014930';

// 別の安定したCORS回避プロキシ(CodeTabs)を使用します
const proxyUrl = 'https://api.codetabs.com/v1/proxy?quest=' + targetApiUrl;

async function fetchAndDisplayData() {
    const statusText = document.getElementById('status');
    try {
        const response = await fetch(proxyUrl);
        if (!response.ok) throw new Error(`通信エラー: ${response.status}`);
        
        // 直接テキストとして取得
        const rawText = await response.text();
        
        const parsedData = parseApiData(rawText);
        
        if (parsedData.length === 0) {
            throw new Error('データが見つからないか、形式が異なります');
        }
        
        renderTable(parsedData);
        
        statusText.innerText = '✅ データの取得と復元が完了しました。';
        statusText.style.color = "#38a169";
    } catch (error) {
        console.error('エラー詳細:', error);
        statusText.innerText = '❌ データの取得に失敗しました。';
        statusText.style.color = "#e53e3e";
    }
}

// 🌐 テキストデータから [日時, 時刻, Payload, RSSI] を抽出する処理
function parseApiData(text) {
    const resultList = [];
    
    // HTMLテーブル形式の場合
    if (text.includes('<table')) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const rows = doc.querySelectorAll('tr');
        
        rows.forEach((row, index) => {
            if (index === 0) return; // ヘッダーをスキップ
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                resultList.push({
                    date: cells[0].innerText.trim(),
                    time: cells[1].innerText.trim(),
                    payload: cells[2].innerText.trim(),
                    rssi: cells[3].innerText.trim()
                });
            }
        });
    } else {
        // プレーンテキスト（タブやスペース区切り）の場合
        const lines = text.split('\n');
        lines.forEach((line, index) => {
            if (index === 0 || line.trim() === '') return;
            const cols = line.trim().split(/\s+/);
            if (cols.length >= 4) {
                resultList.push({
                    date: cols[0],
                    time: cols[1],
                    payload: cols[2],
                    rssi: cols[3]
                });
            }
        });
    }
    return resultList;
}

// 🔧 32文字の1
