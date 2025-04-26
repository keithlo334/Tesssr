import ui

# 創建 WebView 實例
webview = ui.WebView()

# 定義完整的 HTML 內容
html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>速成打字遊戲</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        primary: '#5D5CDE',
                    }
                }
            }
        }
    </script>
    <style>
        @keyframes fallDown {
            0% { transform: translateY(0); }
            100% { transform: translateY(100vh); }
        }
        .word-element {
            position: absolute;
            animation: fallDown linear forwards;
            font-size: 20px;
            padding: 5px 10px;
            border-radius: 5px;
        }
        .word-element.dark {
            color: white;
            background-color: rgba(93, 92, 222, 0.2);
        }
        .word-element.light {
            color: #333;
            background-color: rgba(93, 92, 222, 0.1);
        }
    </style>
</head>
<body class="transition-colors duration-200 bg-white dark:bg-gray-900 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800 dark:text-white">速成打字遊戲</h1>
        
        <!-- 遊戲設定區 -->
        <div class="flex flex-col md:flex-row gap-4 justify-center items-center mb-6">
            <div class="flex items-center space-x-2">
                <label for="gameTime" class="font-medium text-gray-700 dark:text-gray-300">遊戲時間 (秒):</label>
                <input type="number" id="gameTime" min="10" max="300" value="60" class="w-20 border rounded px-2 py-1 text-base bg-white dark:bg-gray-800 text-gray-800 dark:text-white border-gray-300 dark:border-gray-700">
            </div>
            <div class="flex items-center space-x-2">
                <label for="difficulty" class="font-medium text-gray-700 dark:text-gray-300">難度:</label>
                <select id="difficulty" class="border rounded px-2 py-1 text-base bg-white dark:bg-gray-800 text-gray-800 dark:text-white border-gray-300 dark:border-gray-700">
                    <option value="easy">簡單</option>
                    <option value="medium" selected>中等</option>
                    <option value="hard">困難</option>
                </select>
            </div>
            <div class="flex space-x-3">
                <button id="startBtn" class="bg-primary hover:bg-primary/80 text-white px-4 py-2 rounded font-medium transition-colors">開始遊戲</button>
                <button id="restartBtn" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded font-medium transition-colors hidden">重新開始</button>
            </div>
        </div>
        
        <!-- 遊戲資訊區 -->
        <div class="flex justify-between mb-4 max-w-lg mx-auto">
            <div class="text-lg font-semibold text-gray-800 dark:text-white">
                分數: <span id="score">0</span>
            </div>
            <div class="text-lg font-semibold text-gray-800 dark:text-white">
                剩餘時間: <span id="timeLeft">60</span> 秒
            </div>
        </div>
        
        <!-- 遊戲區 -->
        <div id="gameArea" class="relative w-full border-2 border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden" style="height: 60vh; margin: 0 auto;">
            <!-- 落下的單字將在這裡生成 -->
        </div>
        
        <!-- 輸入區 -->
        <div class="max-w-lg mx-auto mt-4">
            <input type="text" id="wordInput" class="w-full border-2 border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2 text-xl bg-white dark:bg-gray-800 text-gray-800 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" placeholder="輸入單字..." autocomplete="off" disabled>
        </div>
        
        <!-- 遊戲結束提示 -->
        <div id="gameOver" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center hidden z-50">
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
                <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-white">遊戲結束!</h2>
                <p class="mb-2 text-gray-700 dark:text-gray-200">你的分數: <span id="finalScore">0</span></p>
                <button id="closeGameOver" class="mt-4 bg-primary hover:bg-primary/80 text-white px-4 py-2 rounded font-medium transition-colors w-full">關閉</button>
            </div>
        </div>
    </div>

    <script>
        // 檢測暗色模式
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.classList.add('dark');
        }
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            if (event.matches) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        });

        // 遊戲狀態和變數
        const gameArea = document.getElementById('gameArea');
        const wordInput = document.getElementById('wordInput');
        const startBtn = document.getElementById('startBtn');
        const restartBtn = document.getElementById('restartBtn');
        const scoreElement = document.getElementById('score');
        const timeLeftElement = document.getElementById('timeLeft');
        const gameOverElement = document.getElementById('gameOver');
        const finalScoreElement = document.getElementById('finalScore');
        const closeGameOverBtn = document.getElementById('closeGameOver');
        const gameTimeInput = document.getElementById('gameTime');
        const difficultySelect = document.getElementById('difficulty');
        
        let gameActive = false;
        let score = 0;
        let timeLeft = 60;
        let gameTimer;
        let wordGenerationTimer;
        let fallingWords = [];
        let wordUpdateInterval;
        
        // 中文常用詞彙庫
        const chineseWords = [
            '你好', '世界', '電腦', '程式', '遊戲', '快樂', '學習', '工作', 
            '朋友', '家庭', '生活', '科技', '未來', '音樂', '運動', '食物',
            '水果', '蔬菜', '動物', '植物', '天空', '大海', '山脈', '河流',
            '城市', '鄉村', '時間', '空間', '知識', '智慧', '經驗', '教育',
            '健康', '環境', '文化', '藝術', '科學', '歷史', '地理', '政治',
            '經濟', '社會', '網路', '電影', '書籍', '旅行', '夢想', '目標'
        ];
        
        const englishWords = [
            'hello', 'world', 'computer', 'program', 'game', 'happy', 'learn', 'work',
            'friend', 'family', 'life', 'tech', 'future', 'music', 'sport', 'food',
            'fruit', 'veggie', 'animal', 'plant', 'sky', 'ocean', 'mountain', 'river',
            'city', 'country', 'time', 'space', 'knowledge', 'wisdom', 'experience', 'education',
            'health', 'environment', 'culture', 'art', 'science', 'history', 'geography', 'politics',
            'economy', 'society', 'internet', 'movie', 'book', 'travel', 'dream', 'goal'
        ];
        
        // 難度設定
        const difficultySettings = {
            easy: {
                fallSpeedMin: 15000,
                fallSpeedMax: 20000,
                wordGenerationInterval: 3000,
                wordPool: chineseWords
            },
            medium: {
                fallSpeedMin: 10000,
                fallSpeedMax: 15000,
                wordGenerationInterval: 2000,
                wordPool: [...chineseWords, ...englishWords]
            },
            hard: {
                fallSpeedMin: 7000,
                fallSpeedMax: 12000,
                wordGenerationInterval: 1500,
                wordPool: englishWords
            }
        };
        
        // 事件監聽器
        startBtn.addEventListener('click', startGame);
        restartBtn.addEventListener('click', restartGame);
        closeGameOverBtn.addEventListener('click', () => {
            gameOverElement.classList.add('hidden');
        });
        
        wordInput.addEventListener('input', checkInput);
        
        // 開始遊戲
        function startGame() {
            // 檢查遊戲時間是否在允許範圍內
            const gameTime = parseInt(gameTimeInput.value);
            if (isNaN(gameTime) || gameTime < 10 || gameTime > 300) {
                alert('請輸入有效的遊戲時間 (10-300 秒)');
                return;
            }
            
            // 重設遊戲狀態
            gameArea.innerHTML = '';
            score = 0;
            timeLeft = gameTime;
            fallingWords = [];
            gameActive = true;
            
            // 更新UI
            scoreElement.textContent = score;
            timeLeftElement.textContent = timeLeft;
            startBtn.classList.add('hidden');
            restartBtn.classList.remove('hidden');
            wordInput.disabled = false;
            wordInput.focus();
            
            // 設定難度
            const difficulty = difficultySelect.value;
            
            // 開始生成單字
            wordGenerationTimer = setInterval(() => {
                if (gameActive) {
                    generateWord(difficultySettings[difficulty]);
                }
            }, difficultySettings[difficulty].wordGenerationInterval);
            
            // 開始計時
            gameTimer = setInterval(() => {
                timeLeft--;
                timeLeftElement.textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    endGame();
                }
            }, 1000);
            
            // 更新落下的單字位置並檢查碰撞
            wordUpdateInterval = setInterval(updateWords, 100);
        }
        
        // 重新開始遊戲
        function restartGame() {
            // 清除所有計時器
            clearInterval(gameTimer);
            clearInterval(wordGenerationTimer);
            clearInterval(wordUpdateInterval);
            
            startGame();
        }
        
        // 生成新單字
        function generateWord(difficultySettings) {
            if (!gameActive) return;
            
            const wordPool = difficultySettings.wordPool;
            const word = wordPool[Math.floor(Math.random() * wordPool.length)];
            
            const wordElement = document.createElement('div');
            wordElement.textContent = word;
            wordElement.className = `word-element ${document.documentElement.classList.contains('dark') ? 'dark' : 'light'}`;
            
            // 設定隨機水平位置
            const gameAreaWidth = gameArea.offsetWidth;
            const wordWidth = word.length * 20 + 20; // 估計寬度
            const maxLeft = gameAreaWidth - wordWidth;
            const left = Math.max(0, Math.floor(Math.random() * maxLeft));
            
            wordElement.style.left = `${left}px`;
            wordElement.style.top = '0';
            
            // 設定隨機下落速度
            const minSpeed = difficultySettings.fallSpeedMin;
            const maxSpeed = difficultySettings.fallSpeedMax;
            const fallSpeed = Math.floor(Math.random() * (maxSpeed - minSpeed + 1)) + minSpeed;
            
            wordElement.style.animationDuration = `${fallSpeed}ms`;
            
            // 將單字加入遊戲區和追蹤陣列
            gameArea.appendChild(wordElement);
            fallingWords.push({
                element: wordElement,
                text: word,
                bottom: 0
            });
        }
        
        // 檢查用戶輸入
        function checkInput() {
            const inputText = wordInput.value.trim();
            
            // 檢查是否有匹配的單字
            const matchIndex = fallingWords.findIndex(wordObj => wordObj.text === inputText);
            
            if (matchIndex !== -1) {
                // 找到匹配的單字,移除它
                const matchedWord = fallingWords[matchIndex];
                matchedWord.element.remove();
                fallingWords.splice(matchIndex, 1);
                
                // 增加分數
                score++;
                scoreElement.textContent = score;
                
                // 清空輸入框
                wordInput.value = '';
            }
        }
        
        // 更新所有單字的位置並檢查是否到達底部
        function updateWords() {
            if (!gameActive) return;
            
            const gameAreaHeight = gameArea.offsetHeight;
            
            fallingWords.forEach((wordObj, index) => {
                const rect = wordObj.element.getBoundingClientRect();
                const gameAreaRect = gameArea.getBoundingClientRect();
                
                // 計算單字底部相對於遊戲區的位置
                const relativeBottom = rect.bottom - gameAreaRect.top;
                wordObj.bottom = relativeBottom;
                
                // 檢查是否到達底部
                if (relativeBottom >= gameAreaHeight) {
                    endGame();
                }
            });
        }
        
        // 結束遊戲
        function endGame() {
            gameActive = false;
            
            // 清除計時器
            clearInterval(gameTimer);
            clearInterval(wordGenerationTimer);
            clearInterval(wordUpdateInterval);
            
            // 更新UI
            wordInput.disabled = true;
            finalScoreElement.textContent = score;
            gameOverElement.classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

# 加載 HTML 內容到 WebView
webview.load_html(html_content)

# 顯示 WebView(全屏顯示)
webview.present('fullscreen')
