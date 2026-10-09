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

// 🔧 32文字の16進数(Payload)を4つの浮動小数点(Float32)に復元する関数
function decodeHexToFloat(hexStr) {
    if (!hexStr || hexStr.length !== 32) return null;
    
    const values = [];
    for (let i = 0; i < 4; i++) {
        const chunk = hexStr.substring(i * 8, i * 8 + 8);
        const buffer = new ArrayBuffer(4);
        const view = new DataView(buffer);
        
        // リトルエンディアンとして1バイトずつセット
        view.setUint8(0, parseInt(chunk.substring(0, 2), 16));
        view.setUint8(1, parseInt(chunk.substring(2, 4), 16));
        view.setUint8(2, parseInt(chunk.substring(4, 6), 16));
        view.setUint8(3, parseInt(chunk.substring(6, 8), 16));
        
        // Float32として読み出し (true = リトルエンディアン)
        values.push(view.getFloat32(0, true));
    }
    
    return {
        lat: values[0],
        lng: values[1],
        val3: values[2],
        alt: values[3]
    };
}

// 📊 画面のテーブルに描画する処理
function renderTable(dataArray) {
    const tableBody = document.querySelector('#data-table tbody');
    tableBody.innerHTML = '';
    
    dataArray.forEach(item => {
        const decoded = decodeHexToFloat(item.payload);
        if (!decoded) return;

        const row = document.createElement('tr');
        const mapLink = `https://www.google.com/maps?q=${decoded.lat},${decoded.lng}`;
        
        row.innerHTML = `
            <td>${item.date}<br><span style="color:#666; font-size:0.85em;">${item.time}</span></td>
            <td>${decoded.lat.toFixed(5)}</td>
            <td>${decoded.lng.toFixed(5)}</td>
            <td>${decoded.val3.toFixed(2)}</td>
            <td>${decoded.alt.toFixed(1)} m</td>
            <td>${item.rssi}</td>
            <td>
                <a href="${mapLink}" target="_blank" class="map-btn">🗺️ マップ</a>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// 実行
fetchAndDisplayData();
