import json

data = []

def make_entry(instruction, thinking, code):
    output = thinking + "\n\n```html\n" + code + "\n```\n\n开发完成！该网页所有功能均已实现，可以直接在浏览器中运行使用。"
    return {"instruction": instruction, "input": "", "output": output}

# 1. 贪吃蛇游戏
data.append(make_entry(
    "使用HTML5 Canvas开发贪吃蛇游戏，支持键盘控制、分数统计、本地存储最高分",
    "我来开发贪吃蛇游戏：\n1. 创建Canvas画布设置游戏区域为400x400像素，网格大小20像素\n2. 定义蛇身数组、食物位置、方向变量，初始化蛇长度为3\n3. 使用setInterval驱动游戏主循环，初始速度120ms每帧\n4. 监听键盘方向键控制移动，防止180度直接转向\n5. 碰撞检测：撞墙或撞到自己身体则游戏结束\n6. 吃到食物时身体增长1节，加10分，速度逐渐加快\n7. 用localStorage保存最高分记录，游戏结束显示得分",
    '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>贪吃蛇</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:Arial}h1{color:#00ff88;margin:10px}#info{color:#fff;margin-bottom:10px;font-size:18px}canvas{border:2px solid #00ff88;border-radius:8px;background:#0f0f23}button{margin-top:15px;padding:10px 25px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold;font-size:16px}</style></head>
<body><h1>🐍 贪吃蛇</h1><div id="info">分数: 0 | 最高: 0</div>
<canvas id="c" width="400" height="400"></canvas><button onclick="init()">重新开始</button>
<script>
const c=document.getElementById('c'),x=c.getContext('2d'),GS=20,TC=c.width/GS;
let sn,fd,dr,nd,sc,hi=+localStorage.getItem('snakeHi')||0,tm,sp;
function init(){sn=[{x:5,y:10},{x:4,y:10},{x:3,y:10}];dr={x:1,y:0};nd={x:1,y:0};sc=0;sp=120;document.getElementById('info').textContent='分数: 0 | 最高: '+hi;spawn();clearInterval(tm);tm=setInterval(up,sp)}
function spawn(){do{fd={x:Math.floor(Math.random()*TC),y:Math.floor(Math.random()*TC)}}while(sn.some(s=>s.x===fd.x&&s.y===fd.y))}
function up(){dr={...nd};const h={x:sn[0].x+dr.x,y:sn[0].y+dr.y};if(h.x<0||h.x>=TC||h.y<0||h.y>=TC||sn.some(s=>s.x===h.x&&s.y===h.y))return end();sn.unshift(h);if(h.x===fd.x&&h.y===fd.y){sc+=10;document.getElementById('info').textContent='分数: '+sc+' | 最高: '+hi;spawn();if(sp>60){sp-=3;clearInterval(tm);tm=setInterval(up,sp)}}else sn.pop();draw()}
function draw(){x.fillStyle='#0f0f23';x.fillRect(0,0,c.width,c.height);x.fillStyle='#e94560';x.beginPath();x.arc(fd.x*GS+GS/2,fd.y*GS+GS/2,GS/2-2,0,Math.PI*2);x.fill();sn.forEach((s,i)=>{x.fillStyle=i?'#00d4ff':'#00ff88';x.fillRect(s.x*GS+1,s.y*GS+1,GS-2,GS-2)})}
function end(){clearInterval(tm);if(sc>hi){hi=sc;localStorage.setItem('snakeHi',hi);document.getElementById('info').textContent='分数: '+sc+' | 最高: '+hi}alert('游戏结束! 得分: '+sc)}
document.addEventListener('keydown',e=>{if(e.key==='ArrowUp'&&dr.y!==1)nd={x:0,y:-1};if(e.key==='ArrowDown'&&dr.y!==-1)nd={x:0,y:1};if(e.key==='ArrowLeft'&&dr.x!==1)nd={x:-1,y:0};if(e.key==='ArrowRight'&&dr.x!==-1)nd={x:1,y:0};e.preventDefault()});init();
</script></body></html>'''
))

# 2. 2048游戏
data.append(make_entry(
    "实现2048数字游戏，支持键盘滑动合并、分数统计、胜负判定",
    "开发2048游戏：\n1. 创建4x4网格布局，使用CSS Grid排列\n2. 初始化时随机在两个空格子生成2或4（90%概率2）\n3. 处理上下左右四个方向的滑动，实现数字移动和合并逻辑\n4. 相同数字碰撞时合并翻倍，分数累加合并后的数值\n5. 每次有效移动后随机在空格生成一个新数字\n6. 任意格子达到2048显示胜利，无空格且无可合并项则失败\n7. 使用localStorage保存最高分记录",
    '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>2048</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#faf8ef;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{font-size:60px;color:#776e65;margin-bottom:10px}.hdr{width:340px;display:flex;justify-content:space-between;margin-bottom:15px;align-items:center}.sc{background:#bbada0;color:#fff;padding:8px 15px;border-radius:5px;text-align:center}.sc span{display:block;font-size:22px;font-weight:bold}.btn{background:#8f7a66;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:bold;font-size:16px}#g{background:#bbada0;border-radius:6px;padding:10px;display:grid;grid-template-columns:repeat(4,70px);gap:10px;position:relative}.cell{width:70px;height:70px;background:rgba(238,228,218,.35);border-radius:3px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:35px}.t2{background:#eee4da;color:#776e65}.t4{background:#ede0c8;color:#776e65}.t8{background:#f2b179;color:#fff}.t16{background:#f59563;color:#fff}.t32{background:#f67c5f;color:#fff}.t64{background:#f65e3b;color:#fff}.t128{background:#edcf72;color:#fff;font-size:30px}.t256{background:#edcc61;color:#fff;font-size:30px}.t512{background:#edc850;color:#fff;font-size:30px}.t1024{background:#edc53f;color:#fff;font-size:25px}.t2048{background:#edc22e;color:#fff;font-size:25px}.msg{position:absolute;inset:0;background:rgba(238,228,218,.7);display:none;flex-direction:column;align-items:center;justify-content:center;border-radius:6px;z-index:10}.msg h2{font-size:50px;color:#776e65;margin-bottom:20px}</style></head>
<body><h1>2048</h1><div class="hdr"><div style="display:flex;gap:10px"><div class="sc">分数<span id="sc">0</span></div><div class="sc">最高<span id="bs">0</span></div></div><button class="btn" onclick="init()">新游戏</button></div><div id="g"><div class="msg" id="mg"><h2 id="mt"></h2><button class="btn" onclick="init()">再来一局</button></div></div>
<script>
let gr,sc=0,bs=+localStorage.getItem('best2048')||0;const g=document.getElementById('g'),mg=document.getElementById('mg'),mt=document.getElementById('mt');
document.getElementById('bs').textContent=bs;
function init(){gr=Array(4).fill().map(()=>Array(4).fill(0));sc=0;document.getElementById('sc').textContent=0;mg.style.display='none';add();add();render()}
function add(){const e=[];for(let i=0;i<4;i++)for(let j=0;j<4;j++)if(!gr[i][j])e.push({i,j});if(e.length){const p=e[Math.floor(Math.random()*e.length)];gr[p.i][p.j]=Math.random()<.9?2:4}}
function render(){g.querySelectorAll('.cell:not(.msg)').forEach(c=>c.remove());for(let i=0;i<4;i++)for(let j=0;j<4;j++){const v=gr[i][j];const d=document.createElement('div');d.className='cell'+(v?' t'+v:'');d.textContent=v||'';g.appendChild(d)}}
function mv(dir){let m=false;for(let i=0;i<4;i++){let ln=[],p=0;for(let j=0;j<4;j++){let r,c;if(dir==='l'){r=i;c=j}else if(dir==='r'){r=i;c=3-j}else if(dir==='u'){r=j;c=i}else{r=3-j;c=i}if(gr[r][c])ln[p++]=gr[r][c]}for(let j=0;j<3;j++)if(ln[j]&&ln[j]===ln[j+1]){ln[j]*=2;sc+=ln[j];ln.splice(j+1,1);ln.push(0)}for(let j=0;j<4;j++){let r,c;if(dir==='l'){r=i;c=j}else if(dir==='r'){r=i;c=3-j}else if(dir==='u'){r=j;c=i}else{r=3-j;c=i}if(gr[r][c]!==ln[j])m=true;gr[r][c]=ln[j]}}if(m){add();render();document.getElementById('sc').textContent=sc;if(sc>bs){bs=sc;localStorage.setItem('best2048',bs);document.getElementById('bs').textContent=bs}if(!canM()){mt.textContent='游戏结束!';mg.style.display='flex'}if(gr.some(r=>r.some(v=>v===2048))){mt.textContent='你赢了!';mg.style.display='flex'}}}
function canM(){for(let i=0;i<4;i++)for(let j=0;j<4;j++){if(!gr[i][j])return true;if(i<3&&gr[i][j]===gr[i+1][j])return true;if(j<3&&gr[i][j]===gr[i][j+1])return true}return false}
document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')mv('l');if(e.key==='ArrowRight')mv('r');if(e.key==='ArrowUp')mv('u');if(e.key==='ArrowDown')mv('d');e.preventDefault()});init();
</script></body></html>'''
))

# 3. 扫雷游戏
data.append(make_entry(
    "经典扫雷游戏，左键翻开、右键标记旗帜、第一次点击安全、数字颜色",
    "开发扫雷游戏：\n1. 创建网格，每个格子初始状态未翻开\n2. 第一次点击后才布雷，确保第一次点击位置周围无雷\n3. 计算每个非雷格子周围8个方向的雷数\n4. 左键翻开格子：雷则游戏结束，数字显示周围雷数，空格递归展开\n5. 右键标记/取消旗帜，阻止误点\n6. 数字用不同颜色：1蓝2绿3红4深蓝5深红6蓝绿7黑8灰\n7. 所有非雷格子翻开则胜利，表情按钮显示游戏状态",
    '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>扫雷</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#c0c0c0;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}.game{background:#c0c0c0;border:3px solid;border-color:#fff #808080 #808080 #fff;padding:10px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding:5px;border:3px solid;border-color:#808080 #fff #fff #808080}.count{background:#000;color:#f00;font-family:'Courier New',monospace;font-size:24px;font-weight:bold;padding:2px 8px;min-width:60px;text-align:center}.face{width:40px;height:40px;font-size:24px;border:3px solid;border-color:#fff #808080 #808080 #fff;background:#c0c0c0;cursor:pointer}.face:active{border-color:#808080 #fff #fff #808080}#board{display:grid;grid-template-columns:repeat(9,30px);gap:0;border:3px solid;border-color:#808080 #fff #fff #808080}.cell{width:30px;height:30px;background:#c0c0c0;border:3px solid;border-color:#fff #808080 #808080 #fff;font-weight:bold;font-size:18px;display:flex;align-items:center;justify-content:center;cursor:pointer}.cell.open{border:1px solid #808080;background:#c0c0c0}.cell.mine{background:#f00}.c1{color:#0000ff}.c2{color:#008000}.c3{color:#ff0000}.c4{color:#000080}.c5{color:#800000}.c6{color:#008080}.c7{color:#000}.c8{color:#808080}</style></head>
<body><div class="game"><div class="top"><div class="count" id="mineCount">10</div><button class="face" id="face" onclick="init()">😊</button><div class="count" id="timer">0</div></div><div id="board"></div></div>
<script>
const ROWS=9,COLS=9,MINES=10;let board,revealed,flagged,gameOver,firstClick,timer,time;
function init(){board=Array(ROWS).fill().map(()=>Array(COLS).fill(0));revealed=Array(ROWS).fill().map(()=>Array(COLS).fill(false));flagged=Array(ROWS).fill().map(()=>Array(COLS).fill(false));gameOver=false;firstClick=true;time=0;clearInterval(timer);document.getElementById('timer').textContent='0';document.getElementById('mineCount').textContent=MINES;document.getElementById('face').textContent='😊';render()}
function render(){const b=document.getElementById('board');b.innerHTML='';for(let i=0;i<ROWS;i++)for(let j=0;j<COLS;j++){const d=document.createElement('div');d.className='cell';if(revealed[i][j]){d.classList.add('open');if(board[i][j]===-1){d.classList.add('mine');d.textContent='💣'}else if(board[i][j]>0){d.classList.add('c'+board[i][j]);d.textContent=board[i][j]}}else if(flagged[i][j]){d.textContent='🚩'}d.addEventListener('click',()=>click(i,j));d.addEventListener('contextmenu',e=>{e.preventDefault();flag(i,j)});b.appendChild(d)}}
function placeMines(sr,sc){let m=0;while(m<MINES){const i=Math.floor(Math.random()*ROWS),j=Math.floor(Math.random()*COLS);if(board[i][j]===-1)continue;if(Math.abs(i-sr)<=1&&Math.abs(j-sc)<=1)continue;board[i][j]=-1;m++}for(let i=0;i<ROWS;i++)for(let j=0;j<COLS;j++)if(board[i][j]!==-1){let c=0;for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const ni=i+di,nj=j+dj;if(ni>=0&&ni<ROWS&&nj>=0&&nj<COLS&&board[ni][nj]===-1)c++}board[i][j]=c}}
function click(i,j){if(gameOver||revealed[i][j]||flagged[i][j])return;if(firstClick){firstClick=false;placeMines(i,j);timer=setInterval(()=>{time++;if(time<=999)document.getElementById('timer').textContent=time},1000)}if(board[i][j]===-1){revealed[i][j]=true;gameOver=true;document.getElementById('face').textContent='😵';clearInterval(timer);for(let x=0;x<ROWS;x++)for(let y=0;y<COLS;y++)if(board[x][y]===-1)revealed[x][y]=true;render();return}reveal(i,j);render();checkWin()}
function reveal(i,j){if(i<0||i>=ROWS||j<0||j>=COLS||revealed[i][j]||flagged[i][j])return;revealed[i][j]=true;if(board[i][j]===0){for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++)if(di||dj)reveal(i+di,j+dj)}}
function flag(i,j){if(gameOver||revealed[i][j])return;flagged[i][j]=!flagged[i][j];let fc=0;for(let x=0;x<ROWS;x++)for(let y=0;y<COLS;y++)if(flagged[x][y])fc++;document.getElementById('mineCount').textContent=MINES-fc;render()}
function checkWin(){let unrevealed=0;for(let i=0;i<ROWS;i++)for(let j=0;j<COLS;j++)if(!revealed[i][j])unrevealed++;if(unrevealed===MINES){gameOver=true;document.getElementById('face').textContent='😎';clearInterval(timer);setTimeout(()=>alert('恭喜你赢了! 用时: '+time+'秒'),100)}}
init();
</script></body></html>'''
))

# 4. 井字棋AI
data.append(make_entry(
    "井字棋游戏，支持双人对战和AI对战（Minimax算法），胜负判定",
    "开发井字棋游戏：\n1. 3x3网格棋盘，点击格子放置棋子\n2. X先手，O后手轮流下棋\n3. 预先定义8种获胜连线（三行三列两对角线）\n4. 检测获胜和平局，获胜时高亮连线\n5. Minimax算法实现AI：递归模拟所有走法，最大化自身最小收益\n6. Alpha-Beta剪枝优化搜索效率\n7. 计分板记录X胜、O胜、平局次数",
    '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>井字棋</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:Arial;color:#fff;padding:20px}h1{margin-bottom:20px;font-size:40px}.mode{margin-bottom:20px;display:flex;gap:10px}.mode button{padding:10px 20px;border:none;border-radius:20px;cursor:pointer;font-weight:bold;background:#fff;color:#667eea}.mode button.active{background:#ffd700;color:#333}.score{display:flex;gap:30px;margin-bottom:20px;font-size:20px}.score span{background:rgba(255,255,255,.2);padding:8px 20px;border-radius:10px}#board{display:grid;grid-template-columns:repeat(3,100px);gap:10px;margin-bottom:20px}.cell{width:100px;height:100px;background:rgba(255,255,255,.9);border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:60px;font-weight:bold;cursor:pointer;transition:transform .2s}.cell:hover{transform:scale(1.05)}.cell.x{color:#e74c3c}.cell.o{color:#3498db}.cell.win{background:#ffd700;animation:pulse .5s infinite}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}#status{font-size:24px;margin-bottom:20px}button.reset{padding:12px 30px;background:#fff;color:#667eea;border:none;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer}</style></head>
<body><h1>⭕ 井字棋 ❌</h1><div class="mode"><button id="pvp" class="active" onclick="setMode('pvp')">双人对战</button><button id="pve" onclick="setMode('pve')">AI对战</button></div><div class="score"><span>X胜: <b id="sx">0</b></span><span>平局: <b id="sd">0</b></span><span>O胜: <b id="so">0</b></span></div><div id="status">X的回合</div><div id="board"></div><button class="reset" onclick="init()">重新开始</button>
<script>
let board,current,gameOver,mode='pvp',scores={x:0,o:0,d:0};
const wins=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
function setMode(m){mode=m;document.getElementById('pvp').classList.toggle('active',m==='pvp');document.getElementById('pve').classList.toggle('active',m==='pve');init()}
function init(){board=Array(9).fill('');current='x';gameOver=false;document.getElementById('status').textContent=current.toUpperCase()+'的回合';render()}
function render(){const b=document.getElementById('b' in window?'board':'board');if(!document.getElementById('board').children.length){for(let i=0;i<9;i++){const c=document.createElement('div');c.className='cell';c.onclick=()=>play(i);document.getElementById('board').appendChild(c)}}document.querySelectorAll('.cell').forEach((c,i)=>{c.textContent=board[i];c.className='cell'+(board[i]?' '+board[i]:'')})}
function play(i){if(gameOver||board[i])return;board[i]=current;if(check(current)){end(current);return}if(board.every(c=>c)){end('d');return}current=current==='x'?'o':'x';document.getElementById('status').textContent=current.toUpperCase()+'的回合';render();if(mode==='pve'&&current==='o'&&!gameOver)setTimeout(aiMove,500)}
function check(p){const wb=document.getElementById('board');return wins.some(([a,b,c])=>{if(board[a]===p&&board[b]===p&&board[c]===p){[a,b,c].forEach(i=>wb.children[i].classList.add('win'));return true}return false})}
function end(w){gameOver=true;if(w==='d'){scores.d++;document.getElementById('sd').textContent=scores.d;document.getElementById('status').textContent='平局!'}else{scores[w]++;document.getElementById(w==='x'?'sx':'so').textContent=scores[w];document.getElementById('status').textContent=w.toUpperCase()+'获胜!'}render()}
function minimax(b,p,alpha,beta){if(wins.some(([a,c,d])=>b[a]==='o'&&b[c]==='o'&&b[d]==='o'))return{score:1};if(wins.some(([a,c,d])=>b[a]==='x'&&b[c]==='x'&&b[d]==='x'))return{score:-1};if(b.every(c=>c))return{score:0};let best=p==='o'?{score:-Infinity}:{score:Infinity};for(let i=0;i<9;i++)if(!b[i]){b[i]=p;const r=minimax(b,p==='o'?'x':'o',alpha,beta);b[i]='';r.idx=i;if(p==='o'){if(r.score>best.score)best=r;alpha=Math.max(alpha,r.score)}else{if(r.score<best.score)best=r;beta=Math.min(beta,r.score)}if(beta<=alpha)break}return best}
function aiMove(){const m=minimax([...board],'o',-Infinity,Infinity);play(m.idx)}
init();
</script></body></html>'''
))

# 继续添加更多条目...
# 我会分批次写入，现在先创建一个基础脚本，然后继续完善

print("开始生成完整数据...")
with open(r'f:\数据集\doubao\cot_data\html\html_cot_3.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"已写入 {len(data)} 条数据")
