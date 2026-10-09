// 対象のAPI URL
const targetApiUrl = 'https://api.buoy.jp/sakura/table.php?lfourId=1014930';
// GitHub PagesのCORSエラーを回避するための無料プロキシ
const proxyUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent(targetApiUrl);

async function fetchAndDisplayData() {
    const statusText = document.getElementById('status');
    try {
        const response = await fetch(proxyUrl);
        if (!response.ok) throw new Error('通信エラー');
        
        const data = await response.json();
        const rawText = data.contents; // プロキシ経由で取得した生のHTMLまたはテキスト
        
        const parsedData = parseApiData(rawText);
        renderTable(parsedData);
        
        statusText.innerText = '✅ データの取得と復元が完了しました。';
        statusText.style.color = "#38a169"; // グリーン
    } catch (error) {
        console.error('エラー:', error);
        statusText.innerText = '❌ データの取得に失敗しました。';
        statusText.style.color = "#e53e3e"; // レッド
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
        // プレーンテキスト（タブ区切り等）の場合
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
    // 32文字(16バイト)以外の場合は処理しない
    if (!hexStr || hexStr.length !== 32) return null;
    
    const values = [];
    
    // 8文字(4バイト)ずつ切り出してFloat32(小数)に変換
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
        val3: values[2], // 温度・速度・HDOPなど
        alt: values[3]   // 標高
    };
}

// 📊 画面のテーブルに描画する処理
function renderTable(dataArray) {
    const tableBody = document.querySelector('#data-table tbody');
    tableBody.innerHTML = '';
    
    dataArray.forEach(item => {
        const decoded = decodeHexToFloat(item.payload);
        if (!decoded) return; // 不正なペイロードはスキップ

        const row = document.createElement('tr');
        
        // Googleマップのリンクを作成
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